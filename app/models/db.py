"""SQLAlchemy ORM models for the MVP."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Stock(Base):
    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    sector: Mapped[str | None] = mapped_column(String(128), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(255), nullable=True)
    exchange: Mapped[str | None] = mapped_column(String(32), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    universe_source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    ohlcv_rows: Mapped[list["OHLCV"]] = relationship(back_populates="stock")
    indicator_rows: Mapped[list["Indicator"]] = relationship(back_populates="stock")
    range_rows: Mapped[list["RangeSnapshot"]] = relationship(back_populates="stock")


class OHLCV(Base):
    __tablename__ = "ohlcv"
    __table_args__ = (UniqueConstraint("stock_id", "timeframe", "bar_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), index=True)
    timeframe: Mapped[str] = mapped_column(String(8), index=True)
    bar_date: Mapped[date] = mapped_column(Date)
    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    adjusted_close: Mapped[float | None] = mapped_column(Float, nullable=True)
    volume: Mapped[float] = mapped_column(Float)
    provider: Mapped[str] = mapped_column(String(64))
    provider_timezone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_complete: Mapped[bool] = mapped_column(Boolean, default=True)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    stock: Mapped["Stock"] = relationship(back_populates="ohlcv_rows")


class Indicator(Base):
    __tablename__ = "indicators"
    __table_args__ = (UniqueConstraint("stock_id", "timeframe", "bar_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), index=True)
    timeframe: Mapped[str] = mapped_column(String(8))
    bar_date: Mapped[date] = mapped_column(Date)
    adx_14: Mapped[float | None] = mapped_column(Float, nullable=True)
    sma_20: Mapped[float | None] = mapped_column(Float, nullable=True)
    sma_20_slope: Mapped[float | None] = mapped_column(Float, nullable=True)
    normalized_sma_20_slope: Mapped[float | None] = mapped_column(Float, nullable=True)
    atr_14: Mapped[float | None] = mapped_column(Float, nullable=True)
    rsi_14: Mapped[float | None] = mapped_column(Float, nullable=True)
    net_drift_30: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_volume_20: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_dollar_volume_20: Mapped[float | None] = mapped_column(Float, nullable=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    stock: Mapped["Stock"] = relationship(back_populates="indicator_rows")


class RangeSnapshot(Base):
    __tablename__ = "ranges"
    __table_args__ = (UniqueConstraint("stock_id", "timeframe", "scan_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), index=True)
    timeframe: Mapped[str] = mapped_column(String(8), index=True)
    scan_date: Mapped[date] = mapped_column(Date, index=True)
    lookback_bars: Mapped[int] = mapped_column(Integer)
    upper_bound: Mapped[float] = mapped_column(Float)
    lower_bound: Mapped[float] = mapped_column(Float)
    support_zone_low: Mapped[float] = mapped_column(Float)
    support_zone_high: Mapped[float] = mapped_column(Float)
    resistance_zone_low: Mapped[float] = mapped_column(Float)
    resistance_zone_high: Mapped[float] = mapped_column(Float)
    midline: Mapped[float] = mapped_column(Float)
    range_width: Mapped[float] = mapped_column(Float)
    atr_14: Mapped[float] = mapped_column(Float)
    latest_close: Mapped[float] = mapped_column(Float)
    touch_count_support: Mapped[int] = mapped_column(Integer)
    touch_count_resistance: Mapped[int] = mapped_column(Integer)
    containment_ratio: Mapped[float] = mapped_column(Float)
    drift_to_range_ratio: Mapped[float] = mapped_column(Float)
    has_recent_breakout: Mapped[bool] = mapped_column(Boolean, default=False)
    qualifies: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    computed_from_bar_date: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    stock: Mapped["Stock"] = relationship(back_populates="range_rows")
    score: Mapped["RangeScore | None"] = relationship(back_populates="range_snapshot", uselist=False)
    setups: Mapped[list["TradeSetup"]] = relationship(back_populates="range_snapshot")


class RangeScore(Base):
    __tablename__ = "range_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    range_id: Mapped[int] = mapped_column(ForeignKey("ranges.id"), unique=True, index=True)
    range_score: Mapped[float] = mapped_column(Float, index=True)
    range_validity_score: Mapped[float] = mapped_column(Float)
    tradeability_score: Mapped[float] = mapped_column(Float)
    opportunity_score: Mapped[float] = mapped_column(Float)
    touch_quality_score: Mapped[float] = mapped_column(Float)
    trend_weakness_score: Mapped[float] = mapped_column(Float)
    containment_quality_score: Mapped[float] = mapped_column(Float)
    width_vs_atr_score: Mapped[float] = mapped_column(Float)
    liquidity_score: Mapped[float] = mapped_column(Float)
    opportunity_location_score: Mapped[float] = mapped_column(Float)
    scored_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    range_snapshot: Mapped["RangeSnapshot"] = relationship(back_populates="score")


class TradeSetup(Base):
    __tablename__ = "trade_setups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    range_id: Mapped[int] = mapped_column(ForeignKey("ranges.id"), index=True)
    setup_direction: Mapped[str] = mapped_column(String(16), index=True)
    setup_status: Mapped[str] = mapped_column(String(16), index=True)
    trigger_bar_date: Mapped[date] = mapped_column(Date, index=True)
    entry_low: Mapped[float] = mapped_column(Float)
    entry_high: Mapped[float] = mapped_column(Float)
    stop_price: Mapped[float] = mapped_column(Float)
    target_1_price: Mapped[float] = mapped_column(Float)
    target_2_price: Mapped[float] = mapped_column(Float)
    rsi_14: Mapped[float | None] = mapped_column(Float, nullable=True)
    rejection_signal: Mapped[str | None] = mapped_column(String(64), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    range_snapshot: Mapped["RangeSnapshot"] = relationship(back_populates="setups")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), index=True)
    range_id: Mapped[int | None] = mapped_column(ForeignKey("ranges.id"), nullable=True)
    trade_setup_id: Mapped[int | None] = mapped_column(ForeignKey("trade_setups.id"), nullable=True)
    alert_type: Mapped[str] = mapped_column(String(32), index=True)
    alert_status: Mapped[str] = mapped_column(String(32), index=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ScanRun(Base):
    __tablename__ = "scan_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timeframe: Mapped[str] = mapped_column(String(8), index=True)
    scan_started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    scan_completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    scan_bar_date: Mapped[date] = mapped_column(Date)
    stocks_processed: Mapped[int] = mapped_column(Integer)
    candles_ingested: Mapped[int] = mapped_column(Integer)
    indicators_computed: Mapped[int] = mapped_column(Integer)
    ranges_detected: Mapped[int] = mapped_column(Integer)
    scores_generated: Mapped[int] = mapped_column(Integer)
    setups_generated: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(16), default="completed")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
