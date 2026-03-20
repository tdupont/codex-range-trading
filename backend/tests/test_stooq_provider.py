from __future__ import annotations

from datetime import date

from app.services.stooq_provider import StooqProvider


def test_stooq_provider_parses_realistic_daily_close() -> None:
    payload = """Date,Open,High,Low,Close,Volume
2026-03-18,218.5,219.0,207.6,208.34,8597000
2026-03-19,208.365,210.425,204.3,205.72,2642218
"""

    bars = StooqProvider._parse_daily_csv(
        ticker="ABBV",
        payload=payload,
        start_date=date(2026, 3, 1),
        end_date=date(2026, 3, 31),
    )

    assert len(bars) == 2
    assert bars[-1].ticker == "ABBV"
    assert bars[-1].trade_date == date(2026, 3, 19)
    assert bars[-1].close == 205.72
    assert bars[-1].adjusted_close == 205.72


def test_stooq_provider_builds_us_symbol_url() -> None:
    assert StooqProvider._build_url("ABBV") == "https://stooq.com/q/d/l/?s=abbv.us&i=d"
