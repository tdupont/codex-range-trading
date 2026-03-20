"""Trade setup generation service."""

from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.config.settings import Settings
from app.models import Indicator, OHLCV, RangeSnapshot, SetupResult, TradeSetup
from app.services.storage_service import StorageService


class SetupService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def build_setups(self, range_row: RangeSnapshot, indicator: Indicator, candle: OHLCV) -> list[SetupResult]:
        atr = float(indicator.atr_14 or 0.0)
        close = float(candle.close)
        open_price = float(candle.open)
        high = float(candle.high)
        low = float(candle.low)
        body = abs(close - open_price)

        bullish_rejection = close > open_price and (min(close, open_price) - low) > body
        bearish_rejection = close < open_price and (high - max(close, open_price)) > body

        long_active = (
            range_row.support_zone_low <= close <= range_row.support_zone_high
            and float(indicator.rsi_14 or 100.0) < 40.0
            and bullish_rejection
        )
        short_active = (
            range_row.resistance_zone_low <= close <= range_row.resistance_zone_high
            and float(indicator.rsi_14 or 0.0) > 60.0
            and bearish_rejection
        )

        return [
            SetupResult(
                setup_direction="long",
                setup_status="active" if long_active else "inactive",
                trigger_bar_date=candle.bar_date,
                entry_low=range_row.support_zone_low,
                entry_high=range_row.support_zone_high,
                stop_price=range_row.support_zone_low - (self.settings.stop_buffer_atr_multiple * atr),
                target_1_price=range_row.midline,
                target_2_price=range_row.resistance_zone_high,
                rsi_14=indicator.rsi_14,
                rejection_signal="bullish_rejection" if bullish_rejection else None,
                notes="Price in support zone with RSI confirmation." if long_active else None,
            ),
            SetupResult(
                setup_direction="short",
                setup_status="active" if short_active else "inactive",
                trigger_bar_date=candle.bar_date,
                entry_low=range_row.resistance_zone_low,
                entry_high=range_row.resistance_zone_high,
                stop_price=range_row.resistance_zone_high + (self.settings.stop_buffer_atr_multiple * atr),
                target_1_price=range_row.midline,
                target_2_price=range_row.support_zone_low,
                rsi_14=indicator.rsi_14,
                rejection_signal="bearish_rejection" if bearish_rejection else None,
                notes="Price in resistance zone with RSI confirmation." if short_active else None,
            ),
        ]

    def generate_for_scan(self, session: Session, timeframe: str, scan_date) -> list[TradeSetup]:
        range_ids = select(RangeSnapshot.id).where(RangeSnapshot.timeframe == timeframe, RangeSnapshot.scan_date == scan_date)
        session.execute(delete(TradeSetup).where(TradeSetup.range_id.in_(range_ids)))
        created: list[TradeSetup] = []
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
            candle = session.scalar(
                select(OHLCV).where(
                    OHLCV.stock_id == snapshot.stock_id,
                    OHLCV.timeframe == timeframe,
                    OHLCV.bar_date == snapshot.computed_from_bar_date,
                )
            )
            if indicator is None or candle is None:
                continue
            for setup in self.build_setups(snapshot, indicator, candle):
                row = TradeSetup(
                    range_id=snapshot.id,
                    setup_direction=setup.setup_direction,
                    setup_status=setup.setup_status,
                    trigger_bar_date=setup.trigger_bar_date,
                    entry_low=setup.entry_low,
                    entry_high=setup.entry_high,
                    stop_price=setup.stop_price,
                    target_1_price=setup.target_1_price,
                    target_2_price=setup.target_2_price,
                    rsi_14=setup.rsi_14,
                    rejection_signal=setup.rejection_signal,
                    notes=setup.notes,
                    created_at=now,
                    updated_at=now,
                )
                session.add(row)
                created.append(row)

        session.flush()
        return created
