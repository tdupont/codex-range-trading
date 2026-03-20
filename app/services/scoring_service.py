"""Range scoring service."""

from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import Indicator, RangeScore, RangeSnapshot, ScoreBreakdown
from app.services.storage_service import StorageService


class ScoringService:
    def score_range(self, range_row: RangeSnapshot, indicator: Indicator) -> ScoreBreakdown:
        total_touches = range_row.touch_count_support + range_row.touch_count_resistance
        touch_raw = min(total_touches / 6.0, 1.0) * 100.0
        trend_raw = max(0.0, min(1.0, (20.0 - float(indicator.adx_14 or 20.0)) / 20.0)) * 100.0
        containment_raw = min(float(range_row.containment_ratio) / 0.95, 1.0) * 100.0
        width_raw = min((float(range_row.range_width) / max(float(range_row.atr_14), 0.01)) / 4.0, 1.0) * 100.0
        liquidity_raw = min(float(indicator.avg_dollar_volume_20 or 0.0) / 50_000_000.0, 1.0) * 100.0

        dist_support = abs(float(range_row.latest_close) - float(range_row.support_zone_high))
        dist_resistance = abs(float(range_row.resistance_zone_low) - float(range_row.latest_close))
        nearest_distance = min(dist_support, dist_resistance)
        half_range = max(float(range_row.range_width) / 2.0, 0.01)
        opportunity_raw = max(0.0, 1.0 - (nearest_distance / half_range)) * 100.0

        touch_quality_score = round(touch_raw * 0.30, 2)
        trend_weakness_score = round(trend_raw * 0.20, 2)
        containment_quality_score = round(containment_raw * 0.15, 2)
        width_vs_atr_score = round(width_raw * 0.15, 2)
        liquidity_score = round(liquidity_raw * 0.10, 2)
        opportunity_location_score = round(opportunity_raw * 0.10, 2)

        range_score = round(
            touch_quality_score
            + trend_weakness_score
            + containment_quality_score
            + width_vs_atr_score
            + liquidity_score
            + opportunity_location_score,
            2,
        )
        range_validity_score = round((touch_raw * 0.40) + (trend_raw * 0.30) + (containment_raw * 0.30), 2)
        tradeability_score = round((width_raw * 0.45) + (liquidity_raw * 0.35) + (containment_raw * 0.20), 2)
        opportunity_score = round((opportunity_raw * 0.60) + (touch_raw * 0.20) + (trend_raw * 0.20), 2)

        return ScoreBreakdown(
            range_score=range_score,
            range_validity_score=range_validity_score,
            tradeability_score=tradeability_score,
            opportunity_score=opportunity_score,
            touch_quality_score=touch_quality_score,
            trend_weakness_score=trend_weakness_score,
            containment_quality_score=containment_quality_score,
            width_vs_atr_score=width_vs_atr_score,
            liquidity_score=liquidity_score,
            opportunity_location_score=opportunity_location_score,
        )

    def score_for_scan(self, session: Session, timeframe: str, scan_date) -> list[RangeScore]:
        snapshot_ids = select(RangeSnapshot.id).where(RangeSnapshot.timeframe == timeframe, RangeSnapshot.scan_date == scan_date)
        session.execute(delete(RangeScore).where(RangeScore.range_id.in_(snapshot_ids)))

        rows: list[RangeScore] = []
        now = StorageService.utc_now()
        snapshots = list(
            session.scalars(
                select(RangeSnapshot).where(
                    RangeSnapshot.timeframe == timeframe,
                    RangeSnapshot.scan_date == scan_date,
                    RangeSnapshot.qualifies.is_(True),
                )
            )
        )

        for snapshot in snapshots:
            indicator = session.scalar(
                select(Indicator).where(
                    Indicator.stock_id == snapshot.stock_id,
                    Indicator.timeframe == timeframe,
                    Indicator.bar_date == snapshot.computed_from_bar_date,
                )
            )
            if indicator is None:
                continue
            score = self.score_range(snapshot, indicator)
            row = RangeScore(
                range_id=snapshot.id,
                range_score=score.range_score,
                range_validity_score=score.range_validity_score,
                tradeability_score=score.tradeability_score,
                opportunity_score=score.opportunity_score,
                touch_quality_score=score.touch_quality_score,
                trend_weakness_score=score.trend_weakness_score,
                containment_quality_score=score.containment_quality_score,
                width_vs_atr_score=score.width_vs_atr_score,
                liquidity_score=score.liquidity_score,
                opportunity_location_score=score.opportunity_location_score,
                scored_at=now,
            )
            session.add(row)
            rows.append(row)

        session.flush()
        return rows
