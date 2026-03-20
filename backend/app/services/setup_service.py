from __future__ import annotations

from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.constants import SETUP_STATUS_ACTIVE, SETUP_STATUS_INACTIVE
from app.core.settings import Settings
from app.models import Indicator, OHLCV, RangeSnapshot, TradeSetup


class SetupService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def run(self, session: Session) -> list[TradeSetup]:
        session.execute(delete(TradeSetup))
        created: list[TradeSetup] = []
        snapshots = list(session.scalars(select(RangeSnapshot).order_by(RangeSnapshot.id.asc())))
        for snapshot in snapshots:
            indicator = session.scalar(
                select(Indicator).where(
                    Indicator.stock_id == snapshot.stock_id,
                    Indicator.trade_date == snapshot.as_of_date,
                )
            )
            candle = session.scalar(
                select(OHLCV).where(
                    OHLCV.stock_id == snapshot.stock_id,
                    OHLCV.trade_date == snapshot.as_of_date,
                )
            )
            if indicator is None or candle is None or indicator.atr_14 is None:
                continue
            long_setup = self._build_long_setup(snapshot, indicator, candle)
            short_setup = self._build_short_setup(snapshot, indicator, candle)
            for setup in [long_setup, short_setup]:
                if setup is not None:
                    session.add(setup)
                    created.append(setup)
        session.flush()
        return created

    def _build_long_setup(self, snapshot: RangeSnapshot, indicator: Indicator, candle: OHLCV) -> TradeSetup | None:
        close = float(candle.close)
        open_price = float(candle.open)
        low = float(candle.low)
        atr = float(indicator.atr_14)
        in_support = float(snapshot.support_zone_low) <= close <= float(snapshot.support_zone_high)
        bullish_rejection = close > open_price and (min(close, open_price) - low) > abs(close - open_price)
        active = in_support and float(indicator.rsi_14 or 0) < 40 and bullish_rejection
        return TradeSetup(
            range_id=snapshot.id,
            stock_id=snapshot.stock_id,
            as_of_date=snapshot.as_of_date,
            direction="long",
            status=SETUP_STATUS_ACTIVE if active else SETUP_STATUS_INACTIVE,
            entry_zone_low=snapshot.support_zone_low,
            entry_zone_high=snapshot.support_zone_high,
            stop_price=_decimal(float(snapshot.support_zone_low) - (self.settings.stop_buffer_atr_multiple * atr)),
            target_1_price=snapshot.midline,
            target_2_price=snapshot.resistance_zone_high,
            rejection_signal="bullish_rejection" if bullish_rejection else None,
            latest_close=snapshot.latest_close,
        )

    def _build_short_setup(self, snapshot: RangeSnapshot, indicator: Indicator, candle: OHLCV) -> TradeSetup | None:
        close = float(candle.close)
        open_price = float(candle.open)
        high = float(candle.high)
        atr = float(indicator.atr_14)
        in_resistance = float(snapshot.resistance_zone_low) <= close <= float(snapshot.resistance_zone_high)
        bearish_rejection = close < open_price and (high - max(close, open_price)) > abs(close - open_price)
        active = in_resistance and float(indicator.rsi_14 or 100) > 60 and bearish_rejection
        return TradeSetup(
            range_id=snapshot.id,
            stock_id=snapshot.stock_id,
            as_of_date=snapshot.as_of_date,
            direction="short",
            status=SETUP_STATUS_ACTIVE if active else SETUP_STATUS_INACTIVE,
            entry_zone_low=snapshot.resistance_zone_low,
            entry_zone_high=snapshot.resistance_zone_high,
            stop_price=_decimal(float(snapshot.resistance_zone_high) + (self.settings.stop_buffer_atr_multiple * atr)),
            target_1_price=snapshot.midline,
            target_2_price=snapshot.support_zone_low,
            rejection_signal="bearish_rejection" if bearish_rejection else None,
            latest_close=snapshot.latest_close,
        )


def _decimal(value: float) -> Decimal:
    return Decimal(f"{value:.6f}")
