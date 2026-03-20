from __future__ import annotations

from threading import Lock

import pytest

from app.services import scan_service as scan_service_module
from app.services.scan_service import ScanAlreadyRunningError, ScanService


class DummySettings:
    default_timeframe = "1d"
    historical_market_data_provider = "local_seed"
    live_quote_provider = "disabled"


class DummyStorage:
    def initialize_database(self) -> None:
        return None


def make_service(monkeypatch: pytest.MonkeyPatch) -> ScanService:
    monkeypatch.setattr(scan_service_module, "build_historical_provider", lambda settings: object())
    monkeypatch.setattr(scan_service_module, "build_live_quote_provider", lambda settings: object())
    return ScanService(DummySettings(), DummyStorage())


def test_run_scan_rejects_overlapping_runs(monkeypatch: pytest.MonkeyPatch) -> None:
    service = make_service(monkeypatch)
    monkeypatch.setattr(service, "_scan_lock", Lock())

    acquired = service._scan_lock.acquire(blocking=False)
    assert acquired is True

    with pytest.raises(ScanAlreadyRunningError):
        service.run_scan("1d")

    service._scan_lock.release()


def test_run_scan_releases_lock_after_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    service = make_service(monkeypatch)
    monkeypatch.setattr(service, "_scan_lock", Lock())

    def blow_up() -> None:
        raise RuntimeError("boom")

    monkeypatch.setattr(service.storage, "initialize_database", blow_up)

    with pytest.raises(RuntimeError, match="boom"):
        service.run_scan("1d")

    assert service._scan_lock.acquire(blocking=False) is True
    service._scan_lock.release()


def test_supported_scan_timeframes_default_to_daily_weekly_monthly() -> None:
    assert DummySettings.default_timeframe == "1d"

    from app.config.settings import Settings

    settings = Settings()
    assert settings.supported_scan_timeframes == ("1d", "1wk", "1mo")
