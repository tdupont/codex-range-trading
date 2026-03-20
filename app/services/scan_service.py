"""End-to-end scan orchestration."""

from __future__ import annotations

import logging
from threading import Lock

from app.config.settings import Settings
from app.models import ScanRun, ScanSummary
from app.services.indicator_service import IndicatorService
from app.services.market_data_service import MarketDataService
from app.services.providers import (
    LocalSeedHistoricalProvider,
    StooqHistoricalProvider,
    StooqLiveQuoteProvider,
)
from app.services.range_detection_service import RangeDetectionService
from app.services.scoring_service import ScoringService
from app.services.setup_service import SetupService
from app.services.storage_service import StorageService
from app.services.universe_service import UniverseService


logger = logging.getLogger(__name__)


class ScanAlreadyRunningError(RuntimeError):
    """Raised when a second scan is started while another scan is still running."""


class ScanService:
    _scan_lock = Lock()

    def __init__(self, settings: Settings, storage: StorageService) -> None:
        self.settings = settings
        self.storage = storage
        self.historical_provider = build_historical_provider(settings)
        self.live_quote_provider = build_live_quote_provider(settings)
        self.universe_service = UniverseService(self.historical_provider)
        self.market_data_service = MarketDataService(settings, self.historical_provider)
        self.indicator_service = IndicatorService(settings)
        self.range_detection_service = RangeDetectionService(settings)
        self.scoring_service = ScoringService()
        self.setup_service = SetupService(settings)

    def run_scan(self, timeframe: str | None = None) -> ScanSummary:
        if not self._scan_lock.acquire(blocking=False):
            raise ScanAlreadyRunningError(
                "A scan is already in progress. Please wait for it to finish before starting another one."
            )

        try:
            timeframe = timeframe or self.settings.default_timeframe
            self.storage.initialize_database()
            started_at = StorageService.utc_now()
            logger.info("Starting scan for timeframe=%s", timeframe)

            with self.storage.session_scope() as session:
                stocks = self.universe_service.refresh(session)
                candles_ingested, scan_bar_date = self.market_data_service.ingest_universe(session, stocks, timeframe)
                indicators_computed = self.indicator_service.compute_for_universe(session, stocks, timeframe)
                self.storage.replace_ranges_for_scan(session, timeframe, scan_bar_date)
                ranges = self.range_detection_service.detect_for_universe(session, stocks, timeframe, scan_bar_date)
                scores = self.scoring_service.score_for_scan(session, timeframe, scan_bar_date)
                setups = self.setup_service.generate_for_scan(session, timeframe, scan_bar_date)

                completed_at = StorageService.utc_now()
                summary = ScanSummary(
                    timeframe=timeframe,
                    scan_started_at=started_at,
                    scan_completed_at=completed_at,
                    scan_bar_date=scan_bar_date,
                    stocks_processed=len([stock for stock in stocks if stock.is_active]),
                    candles_ingested=candles_ingested,
                    indicators_computed=indicators_computed,
                    ranges_detected=len([row for row in ranges if row.qualifies]),
                    scores_generated=len(scores),
                    setups_generated=len(setups),
                )
                session.add(
                    ScanRun(
                        timeframe=timeframe,
                        scan_started_at=started_at,
                        scan_completed_at=completed_at,
                        scan_bar_date=scan_bar_date,
                        stocks_processed=summary.stocks_processed,
                        candles_ingested=summary.candles_ingested,
                        indicators_computed=summary.indicators_computed,
                        ranges_detected=summary.ranges_detected,
                        scores_generated=summary.scores_generated,
                        setups_generated=summary.setups_generated,
                        status="completed",
                        notes=f"Historical provider: {self.settings.historical_market_data_provider}",
                    )
                )
                logger.info(
                    "Completed scan timeframe=%s bar_date=%s qualifying_ranges=%s",
                    timeframe,
                    scan_bar_date,
                    summary.ranges_detected,
                )
                return summary
        finally:
            self._scan_lock.release()


def build_historical_provider(settings: Settings):
    if settings.historical_market_data_provider == "stooq":
        return StooqHistoricalProvider(settings)
    if settings.historical_market_data_provider == "local_seed":
        return LocalSeedHistoricalProvider(settings)
    raise ValueError(
        f"Unsupported historical provider '{settings.historical_market_data_provider}'. "
        "Configure HISTORICAL_MARKET_DATA_PROVIDER as 'stooq' or 'local_seed'."
    )


def build_live_quote_provider(settings: Settings):
    if settings.live_quote_provider in {"stooq", "enabled"}:
        return StooqLiveQuoteProvider(settings)
    if settings.live_quote_provider in {"disabled", "local_seed", "mock"}:
        return StooqLiveQuoteProvider(settings)
    raise ValueError(
        f"Unsupported live quote provider '{settings.live_quote_provider}'. "
        "Configure LIVE_QUOTE_PROVIDER as 'stooq'."
    )
