from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.settings import Settings
from app.services.alert_service import AlertService
from app.services.indicator_service import IndicatorService
from app.services.ingestion_service import IngestionService
from app.services.local_seed_provider import LocalSeedProvider
from app.services.provider import MarketDataProvider
from app.services.range_detection_service import RangeDetectionService
from app.services.scoring_service import ScoringService
from app.services.setup_service import SetupService
from app.services.stooq_provider import StooqProvider
from app.services.universe_service import UniverseService


@dataclass(slots=True)
class ScanSummary:
    stocks_processed: int
    candles_ingested: int
    indicators_computed: int
    ranges_detected: int
    scores_generated: int
    setups_generated: int
    alerts_generated: int


class ScanService:
    def __init__(self, settings: Settings) -> None:
        provider = build_provider(settings)
        self.universe_service = UniverseService(settings, provider)
        self.ingestion_service = IngestionService(provider)
        self.indicator_service = IndicatorService(settings)
        self.range_detection_service = RangeDetectionService(settings)
        self.scoring_service = ScoringService(settings)
        self.setup_service = SetupService(settings)
        self.alert_service = AlertService()
        self.settings = settings

    def run(self, session: Session) -> ScanSummary:
        stocks = self.universe_service.refresh(session)
        candles_ingested = self.ingestion_service.ingest_universe(
            session,
            stocks,
            lookback_days=self.settings.scan_lookback_days,
        )
        indicators_computed = self.indicator_service.compute_for_universe(session, stocks)
        ranges = self.range_detection_service.run_for_universe(session, stocks)
        scores = self.scoring_service.run(session)
        setups = self.setup_service.run(session)
        alerts = self.alert_service.run(session)
        session.commit()
        return ScanSummary(
            stocks_processed=len([stock for stock in stocks if stock.is_active]),
            candles_ingested=candles_ingested,
            indicators_computed=indicators_computed,
            ranges_detected=len(ranges),
            scores_generated=len(scores),
            setups_generated=len(setups),
            alerts_generated=len(alerts),
        )


def build_provider(settings: Settings) -> MarketDataProvider:
    if settings.market_data_provider == "stooq":
        return StooqProvider(settings)
    if settings.market_data_provider == "local_seed":
        return LocalSeedProvider(settings)
    raise ValueError(
        f"Unsupported market data provider '{settings.market_data_provider}'. "
        "For the MVP, configure MARKET_DATA_PROVIDER to 'stooq' or 'local_seed'."
    )
