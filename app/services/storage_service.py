"""SQLite storage and query helpers."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
import logging
from pathlib import Path
from threading import Lock

import pandas as pd
from sqlalchemy import Engine, create_engine, delete, event, func, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import Settings
from app.models import Base, Indicator, OHLCV, RangeScore, RangeSnapshot, ScanRun, Stock, TradeSetup

logger = logging.getLogger(__name__)


class StorageService:
    _init_lock = Lock()
    _initialized_urls: set[str] = set()

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.engine = self._build_engine(settings.database_url)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)

    def _build_engine(self, database_url: str) -> Engine:
        try:
            engine = create_engine(
                database_url,
                connect_args=(
                    {"check_same_thread": False, "timeout": 30}
                    if database_url.startswith("sqlite")
                    else {}
                ),
            )
            if database_url.startswith("sqlite"):
                self._configure_sqlite_engine(engine)
            return engine
        except ModuleNotFoundError as exc:
            fallback_url = "sqlite:///data/range_trading.db"
            logger.warning(
                "Falling back to %s because the configured database driver is unavailable for %s: %s",
                fallback_url,
                database_url,
                exc,
            )
            engine = create_engine(
                fallback_url,
                connect_args={"check_same_thread": False, "timeout": 30},
            )
            self._configure_sqlite_engine(engine)
            return engine

    def initialize_database(self) -> None:
        url_key = str(self.engine.url)
        if url_key in self._initialized_urls:
            return

        if self._sqlite_database_file_exists():
            self._initialized_urls.add(url_key)
            return

        with self._init_lock:
            if url_key in self._initialized_urls:
                return
            if self._sqlite_database_file_exists():
                self._initialized_urls.add(url_key)
                return
            try:
                Base.metadata.create_all(self.engine)
            except OperationalError as exc:
                if "database is locked" not in str(exc).lower():
                    raise
                logger.warning("SQLite database was locked during schema init; retrying once.")
                Base.metadata.create_all(self.engine)
            self._initialized_urls.add(url_key)

    @contextmanager
    def session_scope(self) -> Iterator[Session]:
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def replace_ranges_for_scan(self, session: Session, timeframe: str, scan_date) -> None:
        range_ids = select(RangeSnapshot.id).where(RangeSnapshot.timeframe == timeframe, RangeSnapshot.scan_date == scan_date)
        session.execute(delete(TradeSetup).where(TradeSetup.range_id.in_(range_ids)))
        session.execute(delete(RangeScore).where(RangeScore.range_id.in_(range_ids)))
        session.execute(delete(RangeSnapshot).where(RangeSnapshot.timeframe == timeframe, RangeSnapshot.scan_date == scan_date))

    def latest_scan_run(self, session: Session, timeframe: str) -> ScanRun | None:
        stmt = select(ScanRun).where(ScanRun.timeframe == timeframe).order_by(ScanRun.scan_completed_at.desc()).limit(1)
        return session.scalar(stmt)

    def latest_scan_date(self, session: Session, timeframe: str):
        return session.scalar(select(func.max(RangeSnapshot.scan_date)).where(RangeSnapshot.timeframe == timeframe))

    def screener_dataframe(self, session: Session, timeframe: str) -> pd.DataFrame:
        latest_date = self.latest_scan_date(session, timeframe)
        if latest_date is None:
            return pd.DataFrame()

        stmt = (
            select(
                Stock.ticker,
                Stock.name,
                Stock.sector,
                RangeSnapshot.timeframe,
                RangeSnapshot.scan_date,
                RangeSnapshot.latest_close,
                RangeSnapshot.support_zone_low,
                RangeSnapshot.support_zone_high,
                RangeSnapshot.resistance_zone_low,
                RangeSnapshot.resistance_zone_high,
                RangeSnapshot.midline,
                RangeSnapshot.touch_count_support,
                RangeSnapshot.touch_count_resistance,
                RangeSnapshot.containment_ratio,
                RangeSnapshot.drift_to_range_ratio,
                Indicator.adx_14,
                Indicator.atr_14,
                Indicator.rsi_14,
                Indicator.avg_dollar_volume_20,
                RangeScore.range_score,
                RangeScore.range_validity_score,
                RangeScore.tradeability_score,
                RangeScore.opportunity_score,
                RangeScore.touch_quality_score,
                RangeScore.trend_weakness_score,
                RangeScore.containment_quality_score,
                RangeScore.width_vs_atr_score,
                RangeScore.liquidity_score,
                RangeScore.opportunity_location_score,
                TradeSetup.setup_direction,
                TradeSetup.setup_status,
                TradeSetup.target_1_price,
                TradeSetup.target_2_price,
            )
            .join(RangeSnapshot, RangeSnapshot.stock_id == Stock.id)
            .join(RangeScore, RangeScore.range_id == RangeSnapshot.id)
            .join(
                Indicator,
                (Indicator.stock_id == Stock.id)
                & (Indicator.timeframe == RangeSnapshot.timeframe)
                & (Indicator.bar_date == RangeSnapshot.computed_from_bar_date),
            )
            .outerjoin(
                TradeSetup,
                (TradeSetup.range_id == RangeSnapshot.id) & (TradeSetup.setup_status == "active"),
            )
            .where(
                RangeSnapshot.timeframe == timeframe,
                RangeSnapshot.scan_date == latest_date,
                RangeSnapshot.qualifies.is_(True),
            )
            .order_by(RangeScore.range_score.desc(), Stock.ticker.asc())
        )
        frame = pd.read_sql(stmt, session.bind)
        if frame.empty:
            return frame

        frame.insert(0, "rank", range(1, len(frame) + 1))
        frame["distance_to_support"] = frame["latest_close"] - frame["support_zone_high"]
        frame["distance_to_resistance"] = frame["resistance_zone_low"] - frame["latest_close"]
        frame["opportunity_side"] = frame.apply(
            lambda row: "long"
            if row["distance_to_support"] <= row["distance_to_resistance"]
            else "short",
            axis=1,
        )
        frame["setup_direction"] = frame["setup_direction"].fillna(frame["opportunity_side"])
        frame["setup_status"] = frame["setup_status"].fillna("watch")
        frame["support_zone"] = frame.apply(
            lambda row: f"{row['support_zone_low']:.2f} - {row['support_zone_high']:.2f}", axis=1
        )
        frame["resistance_zone"] = frame.apply(
            lambda row: f"{row['resistance_zone_low']:.2f} - {row['resistance_zone_high']:.2f}", axis=1
        )
        frame["target_summary"] = frame.apply(
            lambda row: (
                f"{row['target_1_price']:.2f} / {row['target_2_price']:.2f}"
                if pd.notna(row["target_1_price"])
                else "-"
            ),
            axis=1,
        )
        return frame

    def latest_detail_context(self, session: Session, ticker: str, timeframe: str) -> dict | None:
        latest_date = self.latest_scan_date(session, timeframe)
        if latest_date is None:
            return None

        stock = session.scalar(select(Stock).where(Stock.ticker == ticker))
        if stock is None:
            return None

        range_row = session.scalar(
            select(RangeSnapshot).where(
                RangeSnapshot.stock_id == stock.id,
                RangeSnapshot.timeframe == timeframe,
                RangeSnapshot.scan_date == latest_date,
                RangeSnapshot.qualifies.is_(True),
            )
        )
        if range_row is None:
            return None

        indicator = session.scalar(
            select(Indicator).where(
                Indicator.stock_id == stock.id,
                Indicator.timeframe == timeframe,
                Indicator.bar_date == range_row.computed_from_bar_date,
            )
        )
        score = session.scalar(select(RangeScore).where(RangeScore.range_id == range_row.id))
        setups = list(
            session.scalars(
                select(TradeSetup).where(TradeSetup.range_id == range_row.id).order_by(TradeSetup.setup_direction.asc())
            )
        )
        bars = list(
            session.scalars(
                select(OHLCV)
                .where(OHLCV.stock_id == stock.id, OHLCV.timeframe == timeframe)
                .order_by(OHLCV.bar_date.desc())
                .limit(120)
            )
        )
        bars.reverse()

        return {
            "stock": stock,
            "range": range_row,
            "indicator": indicator,
            "score": score,
            "setups": setups,
            "bars": bars,
        }

    def available_tickers(self, session: Session, timeframe: str) -> list[str]:
        latest_date = self.latest_scan_date(session, timeframe)
        if latest_date is None:
            return []
        stmt = (
            select(Stock.ticker)
            .join(RangeSnapshot, RangeSnapshot.stock_id == Stock.id)
            .where(
                RangeSnapshot.timeframe == timeframe,
                RangeSnapshot.scan_date == latest_date,
                RangeSnapshot.qualifies.is_(True),
            )
            .order_by(Stock.ticker.asc())
        )
        return list(session.scalars(stmt))

    def scan_runs_dataframe(self, session: Session) -> pd.DataFrame:
        stmt = select(ScanRun).order_by(ScanRun.scan_completed_at.desc()).limit(20)
        return pd.read_sql(stmt, session.bind)

    @staticmethod
    def utc_now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _configure_sqlite_engine(engine: Engine) -> None:
        @event.listens_for(engine, "connect")
        def _set_sqlite_pragmas(dbapi_connection, _connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=30000")
            cursor.close()

    def _sqlite_database_file_exists(self) -> bool:
        if self.engine.url.get_backend_name() != "sqlite":
            return False
        database = self.engine.url.database
        if not database or database == ":memory:":
            return False
        database_path = Path(database)
        if not database_path.is_absolute():
            database_path = self.settings.base_dir / database_path
        return database_path.exists() and database_path.stat().st_size > 0
