from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.settings import Settings
from app.models import Indicator, RangeScore, RangeSnapshot


@dataclass(slots=True)
class ScoreBreakdown:
    touch_quality: float
    trend_weakness: float
    containment_quality: float
    range_width: float
    liquidity: float
    current_opportunity_location: float
    range_validity_score: float
    tradeability_score: float
    opportunity_score: float
    range_score: float


class ScoringService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def score(self, snapshot: RangeSnapshot, indicator: Indicator) -> ScoreBreakdown:
        touch_raw = min((snapshot.support_touch_count + snapshot.resistance_touch_count) / 6, 1.0) * 100
        trend_raw = max(0.0, min(1.0, (20 - float(indicator.adx_14 or 20)) / 20)) * 100
        containment_raw = min(float(snapshot.containment_ratio) / 0.95, 1.0) * 100
        width_raw = min(float(snapshot.range_width_atr_multiple) / 4.0, 1.0) * 100
        liquidity_raw = min(float(indicator.avg_dollar_volume_20 or 0) / 50_000_000, 1.0) * 100
        distance_to_support = abs(float(snapshot.latest_close) - float(snapshot.support_zone_low))
        distance_to_resistance = abs(float(snapshot.latest_close) - float(snapshot.resistance_zone_high))
        zone_span = max(float(snapshot.range_width), 0.01)
        opportunity_raw = max(0.0, 1 - min(distance_to_support, distance_to_resistance) / zone_span) * 100

        touch_quality = touch_raw * 0.30
        trend_weakness = trend_raw * 0.20
        containment_quality = containment_raw * 0.15
        range_width = width_raw * 0.15
        liquidity = liquidity_raw * 0.10
        current_opportunity_location = opportunity_raw * 0.10

        range_validity_score = ((touch_raw * 0.45) + (trend_raw * 0.30) + (containment_raw * 0.25))
        tradeability_score = ((width_raw * 0.45) + (liquidity_raw * 0.35) + (touch_raw * 0.20))
        opportunity_score = ((opportunity_raw * 0.60) + (trend_raw * 0.20) + (containment_raw * 0.20))
        range_score = (
            touch_quality
            + trend_weakness
            + containment_quality
            + range_width
            + liquidity
            + current_opportunity_location
        )
        return ScoreBreakdown(
            touch_quality=round(touch_quality, 2),
            trend_weakness=round(trend_weakness, 2),
            containment_quality=round(containment_quality, 2),
            range_width=round(range_width, 2),
            liquidity=round(liquidity, 2),
            current_opportunity_location=round(current_opportunity_location, 2),
            range_validity_score=round(range_validity_score, 2),
            tradeability_score=round(tradeability_score, 2),
            opportunity_score=round(opportunity_score, 2),
            range_score=round(range_score, 2),
        )

    def run(self, session: Session) -> list[RangeScore]:
        session.execute(delete(RangeScore))
        created: list[RangeScore] = []
        snapshots = list(session.scalars(select(RangeSnapshot).order_by(RangeSnapshot.id.asc())))
        for snapshot in snapshots:
            indicator = session.scalar(
                select(Indicator).where(
                    Indicator.stock_id == snapshot.stock_id,
                    Indicator.trade_date == snapshot.as_of_date,
                )
            )
            if indicator is None:
                continue
            score = self.score(snapshot, indicator)
            row = RangeScore(
                range_id=snapshot.id,
                range_score=_decimal(score.range_score),
                range_validity_score=_decimal(score.range_validity_score, 2),
                tradeability_score=_decimal(score.tradeability_score, 2),
                opportunity_score=_decimal(score.opportunity_score, 2),
                touch_quality_score=_decimal(score.touch_quality, 2),
                trend_weakness_score=_decimal(score.trend_weakness, 2),
                containment_quality_score=_decimal(score.containment_quality, 2),
                range_width_score=_decimal(score.range_width, 2),
                liquidity_score=_decimal(score.liquidity, 2),
                current_opportunity_location_score=_decimal(score.current_opportunity_location, 2),
                scoring_version=self.settings.scoring_version,
            )
            session.add(row)
            created.append(row)
        session.flush()
        return created


def _decimal(value: float, places: int = 2) -> Decimal:
    return Decimal(f"{value:.{places}f}")
