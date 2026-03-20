from __future__ import annotations

from decimal import Decimal

import numpy as np
import pandas as pd
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.settings import Settings
from app.models import Indicator, OHLCV, Stock


class IndicatorService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _build_indicator_frame(self, candles: list[OHLCV]) -> pd.DataFrame:
        frame = pd.DataFrame(
            {
                "trade_date": [candle.trade_date for candle in candles],
                "open": [float(candle.open) for candle in candles],
                "high": [float(candle.high) for candle in candles],
                "low": [float(candle.low) for candle in candles],
                "close": [float(candle.close) for candle in candles],
                "volume": [candle.volume for candle in candles],
            }
        ).sort_values("trade_date")
        frame["sma_20"] = frame["close"].rolling(self.settings.sma_period).mean()
        frame["atr_14"] = _atr(frame, self.settings.atr_period)
        frame["adx_14"] = _adx(frame, self.settings.adx_period)
        frame["rsi_14"] = _rsi(frame["close"], self.settings.rsi_period)
        frame["avg_dollar_volume_20"] = (frame["close"] * frame["volume"]).rolling(20).mean()
        frame["sma_20_slope"] = (
            frame["sma_20"].diff().rolling(5).mean() / frame["close"].replace(0, pd.NA)
        ).abs()
        return frame

    def compute_for_stock(self, session: Session, stock: Stock) -> int:
        candles = list(
            session.scalars(
                select(OHLCV).where(OHLCV.stock_id == stock.id).order_by(OHLCV.trade_date.asc())
            )
        )
        if len(candles) < max(self.settings.sma_period, self.settings.atr_period, self.settings.adx_period):
            return 0

        frame = self._build_indicator_frame(candles)
        session.execute(delete(Indicator).where(Indicator.stock_id == stock.id))
        rows = []
        for row in frame.itertuples(index=False):
            rows.append(
                Indicator(
                    stock_id=stock.id,
                    trade_date=row.trade_date,
                    sma_20=_to_decimal(row.sma_20),
                    sma_20_slope=_to_decimal(row.sma_20_slope),
                    atr_14=_to_decimal(row.atr_14),
                    adx_14=_to_decimal(row.adx_14),
                    rsi_14=_to_decimal(row.rsi_14),
                    avg_dollar_volume_20=_to_decimal(row.avg_dollar_volume_20, places=2),
                )
            )
        session.add_all(rows)
        session.flush()
        return len(rows)

    def compute_for_universe(self, session: Session, stocks: list[Stock]) -> int:
        total = 0
        for stock in stocks:
            if stock.is_active:
                total += self.compute_for_stock(session, stock)
        return total


def _to_decimal(value: float | None, places: int = 6) -> Decimal | None:
    if value is None or pd.isna(value):
        return None
    return Decimal(f"{float(value):.{places}f}")


def _atr(frame: pd.DataFrame, period: int) -> pd.Series:
    prev_close = frame["close"].shift(1)
    true_range = pd.concat(
        [
            frame["high"] - frame["low"],
            (frame["high"] - prev_close).abs(),
            (frame["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return true_range.ewm(alpha=1 / period, adjust=False).mean()


def _rsi(close: pd.Series, period: int) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def _adx(frame: pd.DataFrame, period: int) -> pd.Series:
    high = frame["high"]
    low = frame["low"]
    close = frame["close"]
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)

    prev_close = close.shift(1)
    tr = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr = tr.ewm(alpha=1 / period, adjust=False).mean()
    plus_di = 100 * (plus_dm.ewm(alpha=1 / period, adjust=False).mean() / atr.replace(0, np.nan))
    minus_di = 100 * (minus_dm.ewm(alpha=1 / period, adjust=False).mean() / atr.replace(0, np.nan))
    dx = ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)) * 100
    return dx.ewm(alpha=1 / period, adjust=False).mean()
