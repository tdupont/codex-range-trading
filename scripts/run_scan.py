"""CLI entry point to run a local scan."""

from __future__ import annotations

from app.config.logging import configure_logging
from app.config.settings import settings
from app.services.scan_service import ScanService
from app.services.storage_service import StorageService


def main() -> None:
    configure_logging(settings.log_level)
    storage = StorageService(settings)
    service = ScanService(settings, storage)
    summary = service.run_scan(settings.default_timeframe)
    print(
        "Completed scan:",
        {
            "timeframe": summary.timeframe,
            "scan_bar_date": str(summary.scan_bar_date),
            "stocks_processed": summary.stocks_processed,
            "candles_ingested": summary.candles_ingested,
            "indicators_computed": summary.indicators_computed,
            "ranges_detected": summary.ranges_detected,
            "scores_generated": summary.scores_generated,
            "setups_generated": summary.setups_generated,
        },
    )


if __name__ == "__main__":
    main()
