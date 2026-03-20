"""Indicator calculation service using pandas and numpy."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.config.settings import Settings
from app.models import Indicator, OHLCV, Stock
from app.services.storage_service import StorageService


class IndicatorService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def compute_for_universe(self, session: Session, stocks: list[Stock], timeframe: str) -> int:
        computed = 0
        for stock in stocks:
            if not stock.is_active:
                continue
            computed += self.compute_for_stock(session, stock, timeframe)
        return computed

    def compute_for_stock(self, session: Session, stock: Stock, timeframe: str) -> int:
        candles = list(
            session.query(OHLCV)
            .filter(OHLCV.stock_id == stock.id, OHLCV.timeframe == timeframe, OHLCV.is_complete.is_(True))
            .order_by(OHLCV.bar_date.asc())
        )
        if len(candles) < max(self.settings.range_lookback_bars, self.settings.sma_period, self.settings.adx_period):
            return 0

        frame = pd.DataFrame(
            {
                "bar_date": [row.bar_date for row in candles],
                "open": [row.open for row in candles],
                "high": [row.high for row in candles],
                "low": [row.low for row in candles],
                "close": [row.close for row in candles],
                "volume": [row.volume for row in candles],
            }
        )
        indicator_frame = self.build_indicator_frame(frame)

        session.execute(delete(Indicator).where(Indicator.stock_id == stock.id, Indicator.timeframe == timeframe))
        now = StorageService.utc_now()
        rows = 0
        for row in indicator_frame.itertuples(index=False):
            session.add(
                Indicator(
                    stock_id=stock.id,
                    timeframe=timeframe,
                    bar_date=row.bar_date,
                    adx_14=_safe_float(row.adx_14),
                    sma_20=_safe_float(row.sma_20),
                    sma_20_slope=_safe_float(row.sma_20_slope),
                    normalized_sma_20_slope=_safe_float(row.normalized_sma_20_slope),
                    atr_14=_safe_float(row.atr_14),
                    rsi_14=_safe_float(row.rsi_14),
                    net_drift_30=_safe_float(row.net_drift_30),
                    avg_volume_20=_safe_float(row.avg_volume_20),
                    avg_dollar_volume_20=_safe_float(row.avg_dollar_volume_20),
                    computed_at=now,
                )
            )
            rows += 1
        session.flush()
        return rows

    def build_indicator_frame(self, frame: pd.DataFrame) -> pd.DataFrame:
        out = frame.copy().sort_values("bar_date").reset_index(drop=True)
        out["sma_20"] = out["close"].rolling(self.settings.sma_period).mean()
        out["atr_14"] = _atr(out, self.settings.atr_period)
        out["adx_14"] = _adx(out, self.settings.adx_period)
        out["rsi_14"] = _rsi(out["close"], self.settings.rsi_period)
        out["avg_volume_20"] = out["volume"].rolling(self.settings.liquidity_lookback_bars).mean()
        out["avg_dollar_volume_20"] = (out["close"] * out["volume"]).rolling(self.settings.liquidity_lookback_bars).mean()
        out["sma_20_slope"] = out["sma_20"].diff(5) / 5.0
        out["normalized_sma_20_slope"] = (out["sma_20_slope"] / out["atr_14"].replace(0, np.nan)).abs()
        out["net_drift_30"] = out["close"] - out["close"].shift(self.settings.range_lookback_bars - 1)
        return out


def _safe_float(value) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value)


def _atr(frame: pd.DataFrame, period: int) -> pd.Series:
    high = frame["high"]
    low = frame["low"]
    close = frame["close"]
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False).mean()


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
