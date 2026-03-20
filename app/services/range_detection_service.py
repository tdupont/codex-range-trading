"""Rule-based range detection service."""

from __future__ import annotations

import pandas as pd
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.config.settings import Settings
from app.models import Indicator, OHLCV, RangeDetectionResult, RangeSnapshot, Stock
from app.services.storage_service import StorageService


class RangeDetectionService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def detect_for_universe(self, session: Session, stocks: list[Stock], timeframe: str, scan_date) -> list[RangeSnapshot]:
        session.execute(delete(RangeSnapshot).where(RangeSnapshot.timeframe == timeframe, RangeSnapshot.scan_date == scan_date))
        created: list[RangeSnapshot] = []
        now = StorageService.utc_now()

        for stock in stocks:
            if not stock.is_active:
                continue

            bars = list(
                session.scalars(
                    select(OHLCV)
                    .where(OHLCV.stock_id == stock.id, OHLCV.timeframe == timeframe, OHLCV.is_complete.is_(True))
                    .order_by(OHLCV.bar_date.asc())
                )
            )
            indicator = session.scalar(
                select(Indicator)
                .where(Indicator.stock_id == stock.id, Indicator.timeframe == timeframe)
                .order_by(Indicator.bar_date.desc())
                .limit(1)
            )
            if len(bars) < self.settings.range_lookback_bars or indicator is None or indicator.atr_14 is None:
                continue

            frame = pd.DataFrame(
                {
                    "bar_date": [bar.bar_date for bar in bars],
                    "open": [bar.open for bar in bars],
                    "high": [bar.high for bar in bars],
                    "low": [bar.low for bar in bars],
                    "close": [bar.close for bar in bars],
                }
            )
            result = self.analyze_frame(frame, indicator)
            snapshot = RangeSnapshot(
                stock_id=stock.id,
                timeframe=timeframe,
                scan_date=scan_date,
                lookback_bars=result.lookback_bars,
                upper_bound=result.upper_bound,
                lower_bound=result.lower_bound,
                support_zone_low=result.support_zone_low,
                support_zone_high=result.support_zone_high,
                resistance_zone_low=result.resistance_zone_low,
                resistance_zone_high=result.resistance_zone_high,
                midline=result.midline,
                range_width=result.range_width,
                atr_14=result.atr_14,
                latest_close=result.latest_close,
                touch_count_support=result.touch_count_support,
                touch_count_resistance=result.touch_count_resistance,
                containment_ratio=result.containment_ratio,
                drift_to_range_ratio=result.drift_to_range_ratio,
                has_recent_breakout=result.has_recent_breakout,
                qualifies=result.qualifies,
                rejection_reason=result.rejection_reason,
                computed_from_bar_date=result.scan_date,
                created_at=now,
            )
            session.add(snapshot)
            created.append(snapshot)

        session.flush()
        return created

    def analyze_frame(self, frame: pd.DataFrame, indicator: Indicator) -> RangeDetectionResult:
        lookback = frame.tail(self.settings.range_lookback_bars).reset_index(drop=True)
        atr = float(indicator.atr_14 or 0.0)
        latest_close = float(lookback["close"].iloc[-1])
        upper_bound = float(lookback["high"].max())
        lower_bound = float(lookback["low"].min())
        range_width = upper_bound - lower_bound
        support_zone_low = lower_bound
        support_zone_high = lower_bound + (self.settings.zone_atr_multiple * atr)
        resistance_zone_low = upper_bound - (self.settings.zone_atr_multiple * atr)
        resistance_zone_high = upper_bound
        midline = (upper_bound + lower_bound) / 2.0
        containment_ratio = float(lookback["close"].between(lower_bound, upper_bound).mean())
        touch_count_support = self._count_touches(lookback, "support", lower_bound, support_zone_high, atr)
        touch_count_resistance = self._count_touches(lookback, "resistance", resistance_zone_low, upper_bound, atr)
        normalized_slope = float(abs(indicator.normalized_sma_20_slope or 0.0))
        adx_14 = float(indicator.adx_14 or 999.0)
        net_drift = float(indicator.net_drift_30 or 0.0)
        drift_ratio = abs(net_drift) / range_width if range_width > 0 else 999.0
        width_vs_atr = range_width / atr if atr > 0 else 0.0
        recent_breakout = self._has_recent_breakout(lookback, lower_bound, upper_bound)

        conditions: list[tuple[bool, str]] = [
            (adx_14 < 20.0, "ADX(14) must be below 20"),
            (normalized_slope <= self.settings.max_normalized_sma_slope, "Normalized SMA(20) slope too large"),
            (touch_count_support >= self.settings.min_touch_count, "Not enough support touches"),
            (touch_count_resistance >= self.settings.min_touch_count, "Not enough resistance touches"),
            (width_vs_atr >= self.settings.min_range_width_atr_multiple, "Range width is too narrow vs ATR"),
            (drift_ratio <= self.settings.max_drift_to_range_ratio, "Net drift is too large relative to range width"),
            (not recent_breakout, "Recent breakout close outside the range"),
        ]
        rejection_reason = next((reason for passed, reason in conditions if not passed), None)

        return RangeDetectionResult(
            qualifies=rejection_reason is None,
            rejection_reason=rejection_reason,
            scan_date=lookback["bar_date"].iloc[-1],
            lookback_bars=self.settings.range_lookback_bars,
            upper_bound=upper_bound,
            lower_bound=lower_bound,
            support_zone_low=support_zone_low,
            support_zone_high=support_zone_high,
            resistance_zone_low=resistance_zone_low,
            resistance_zone_high=resistance_zone_high,
            midline=midline,
            range_width=range_width,
            atr_14=atr,
            latest_close=latest_close,
            touch_count_support=touch_count_support,
            touch_count_resistance=touch_count_resistance,
            containment_ratio=containment_ratio,
            drift_to_range_ratio=drift_ratio,
            has_recent_breakout=recent_breakout,
            normalized_sma_20_slope=normalized_slope,
            adx_14=adx_14,
            rsi_14=indicator.rsi_14,
        )

    def _count_touches(self, frame: pd.DataFrame, side: str, zone_low: float, zone_high: float, atr: float) -> int:
        tolerance = self.settings.touch_tolerance_atr_multiple * atr
        probe_col = "low" if side == "support" else "high"
        count = 0
        last_touch_idx = -1_000
        for idx, row in frame.iterrows():
            probe = float(row[probe_col])
            close = float(row["close"])
            in_zone = (
                zone_low - tolerance <= probe <= zone_high + tolerance
                or zone_low - tolerance <= close <= zone_high + tolerance
            )
            if in_zone and idx - last_touch_idx >= self.settings.touch_separation_bars:
                count += 1
                last_touch_idx = idx
        return count

    def _has_recent_breakout(self, frame: pd.DataFrame, lower_bound: float, upper_bound: float) -> bool:
        recent = frame.tail(self.settings.recent_breakout_lookback_bars)
        return bool(((recent["close"] < lower_bound) | (recent["close"] > upper_bound)).any())
