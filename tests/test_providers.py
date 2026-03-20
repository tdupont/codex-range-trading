from __future__ import annotations

from datetime import date

from app.config.settings import Settings
from app.services.providers import LocalSeedHistoricalProvider


def test_local_seed_provider_supports_weekly_timeframe() -> None:
    provider = LocalSeedHistoricalProvider(Settings(historical_market_data_provider="local_seed"))

    bars = provider.get_ohlcv("AAPL", "1wk", date(2024, 1, 1), date(2024, 6, 30))

    assert bars
    assert all(bar.timeframe == "1wk" for bar in bars)
    assert all(bar.bar_date.weekday() == 4 for bar in bars)


def test_local_seed_provider_supports_monthly_timeframe() -> None:
    provider = LocalSeedHistoricalProvider(Settings(historical_market_data_provider="local_seed"))

    bars = provider.get_ohlcv("MSFT", "1mo", date(2023, 1, 1), date(2025, 12, 31))

    assert bars
    assert all(bar.timeframe == "1mo" for bar in bars)
    assert len({(bar.bar_date.year, bar.bar_date.month) for bar in bars}) == len(bars)
