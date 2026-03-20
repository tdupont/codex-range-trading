from __future__ import annotations

from datetime import date

from app.services.providers import StooqHistoricalProvider, StooqLiveQuoteProvider


def test_stooq_historical_provider_parses_daily_csv() -> None:
    payload = """Date,Open,High,Low,Close,Volume
2026-03-18,218.5,219.0,207.6,208.34,8597000
2026-03-19,208.365,210.425,204.3,205.72,2642218
"""
    bars = StooqHistoricalProvider._parse_daily_csv("ABBV", payload, date(2026, 3, 1), date(2026, 3, 31))

    assert len(bars) == 2
    assert bars[-1].ticker == "ABBV"
    assert bars[-1].bar_date == date(2026, 3, 19)
    assert bars[-1].close == 205.72


def test_stooq_quote_url_targets_stooq_csv_endpoint() -> None:
    assert (
        StooqLiveQuoteProvider._build_quote_url("ABBV")
        == "https://stooq.com/q/l/?s=abbv.us&f=sd2t2ohlcvn&e=csv"
    )


def test_stooq_quote_parser_supports_headerless_payload() -> None:
    payload = "ABBV.US,2026-03-19,21:03:35,208.365,210.425,204.3,206.23,7006809,ABBVIE INC\n"
    row = StooqLiveQuoteProvider._parse_quote_csv(payload)

    assert row["symbol"] == "ABBV.US"
    assert row["close"] == "206.23"
