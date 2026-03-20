from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import pandas as pd
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.settings import Settings
from app.models import Indicator, OHLCV, RangeSnapshot, Stock


@dataclass(slots=True)
class RangeDetectionResult:
    qualified: bool
    as_of_date: date
    lookback_days: int
    upper_bound: float
    lower_bound: float
    midline: float
    range_width: float
    range_width_atr_multiple: float
    support_zone_low: float
    support_zone_high: float
    resistance_zone_low: float
    resistance_zone_high: float
    containment_ratio: float
    support_touch_count: int
    resistance_touch_count: int
    latest_close: float
    notes: dict[str, float | bool | int]


class RangeDetectionService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def analyze_frame(self, frame: pd.DataFrame, indicator: Indicator) -> RangeDetectionResult:
        lookback = frame.tail(self.settings.range_lookback_days).copy()
        upper_bound = float(lookback["high"].max())
        lower_bound = float(lookback["low"].min())
        atr = float(indicator.atr_14 or 0)
        midline = (upper_bound + lower_bound) / 2
        range_width = upper_bound - lower_bound
        support_zone_high = lower_bound + (self.settings.zone_atr_multiple * atr)
        resistance_zone_low = upper_bound - (self.settings.zone_atr_multiple * atr)
        containment_ratio = float(lookback["close"].between(lower_bound, upper_bound).mean())
        support_touch_count = _count_zone_touches(
            lookback,
            zone_low=lower_bound,
            zone_high=support_zone_high,
            column_pair=("low", "close"),
            cooldown_days=self.settings.touch_cooldown_days,
            midline=midline,
        )
        resistance_touch_count = _count_zone_touches(
            lookback,
            zone_low=resistance_zone_low,
            zone_high=upper_bound,
            column_pair=("high", "close"),
            cooldown_days=self.settings.touch_cooldown_days,
            midline=midline,
        )
        sma_slope = float(indicator.sma_20_slope or 0)
        adx = float(indicator.adx_14 or 999)
        width_multiple = range_width / atr if atr else 0
        latest_close = float(lookback["close"].iloc[-1])
        qualified = all(
            [
                adx < 20,
                sma_slope < self.settings.max_sma20_slope_abs,
                containment_ratio >= self.settings.containment_threshold,
                support_touch_count >= self.settings.min_touch_count,
                resistance_touch_count >= self.settings.min_touch_count,
                width_multiple >= self.settings.min_range_width_atr_multiple,
            ]
        )
        return RangeDetectionResult(
            qualified=qualified,
            as_of_date=lookback["trade_date"].iloc[-1],
            lookback_days=self.settings.range_lookback_days,
            upper_bound=upper_bound,
            lower_bound=lower_bound,
            midline=midline,
            range_width=range_width,
            range_width_atr_multiple=width_multiple,
            support_zone_low=lower_bound,
            support_zone_high=support_zone_high,
            resistance_zone_low=resistance_zone_low,
            resistance_zone_high=upper_bound,
            containment_ratio=containment_ratio,
            support_touch_count=support_touch_count,
            resistance_touch_count=resistance_touch_count,
            latest_close=latest_close,
            notes={
                "adx_pass": adx < 20,
                "adx_14": adx,
                "sma_slope_pass": sma_slope < self.settings.max_sma20_slope_abs,
                "sma_20_slope": sma_slope,
                "containment_pass": containment_ratio >= self.settings.containment_threshold,
                "width_pass": width_multiple >= self.settings.min_range_width_atr_multiple,
            },
        )

    def run_for_universe(self, session: Session, stocks: list[Stock]) -> list[RangeSnapshot]:
        session.execute(delete(RangeSnapshot))
        created: list[RangeSnapshot] = []
        for stock in stocks:
            if not stock.is_active:
                continue
            candles = list(
                session.execute(
                    select(OHLCV, Indicator)
                    .join(Indicator, (Indicator.stock_id == OHLCV.stock_id) & (Indicator.trade_date == OHLCV.trade_date))
                    .where(OHLCV.stock_id == stock.id)
                    .order_by(OHLCV.trade_date.asc())
                ).all()
            )
            if len(candles) < self.settings.range_lookback_days:
                continue
            candle_frame = pd.DataFrame(
                [
                    {
                        "trade_date": ohlcv.trade_date,
                        "open": float(ohlcv.open),
                        "high": float(ohlcv.high),
                        "low": float(ohlcv.low),
                        "close": float(ohlcv.close),
                    }
                    for ohlcv, _ in candles
                ]
            )
            latest_indicator = candles[-1][1]
            result = self.analyze_frame(candle_frame, latest_indicator)
            if not result.qualified:
                continue
            snapshot = RangeSnapshot(
                stock_id=stock.id,
                as_of_date=result.as_of_date,
                lookback_days=result.lookback_days,
                upper_bound=_decimal(result.upper_bound),
                lower_bound=_decimal(result.lower_bound),
                midline=_decimal(result.midline),
                range_width=_decimal(result.range_width),
                range_width_atr_multiple=_decimal(result.range_width_atr_multiple),
                support_zone_low=_decimal(result.support_zone_low),
                support_zone_high=_decimal(result.support_zone_high),
                resistance_zone_low=_decimal(result.resistance_zone_low),
                resistance_zone_high=_decimal(result.resistance_zone_high),
                containment_ratio=_decimal(result.containment_ratio),
                support_touch_count=result.support_touch_count,
                resistance_touch_count=result.resistance_touch_count,
                latest_close=_decimal(result.latest_close),
                qualified=True,
                notes_json=result.notes,
            )
            session.add(snapshot)
            created.append(snapshot)
        session.flush()
        return created


def _count_zone_touches(
    frame: pd.DataFrame,
    zone_low: float,
    zone_high: float,
    column_pair: tuple[str, str],
    cooldown_days: int,
    midline: float,
) -> int:
    count = 0
    cooldown = cooldown_days + 1
    last_touch_index = -cooldown
    probe_a, probe_b = column_pair
    for idx, row in enumerate(frame.itertuples(index=False)):
        in_zone = zone_low <= getattr(row, probe_a) <= zone_high or zone_low <= getattr(row, probe_b) <= zone_high
        moved_away = abs(getattr(row, probe_b) - midline) <= abs(zone_high - zone_low) + abs(midline - zone_low) / 2
        if in_zone and idx - last_touch_index > cooldown_days:
            count += 1
            last_touch_index = idx
        elif in_zone and moved_away and idx - last_touch_index > 0:
            count += 1
            last_touch_index = idx
    return count


def _decimal(value: float) -> Decimal:
    return Decimal(f"{value:.6f}")
