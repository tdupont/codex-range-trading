from __future__ import annotations

from datetime import date, timedelta

import pandas as pd

from app.config.settings import Settings
from app.services.indicator_service import IndicatorService


def test_indicator_frame_contains_required_columns() -> None:
    settings = Settings()
    service = IndicatorService(settings)
    start = date(2025, 1, 1)
    rows = []
    for idx in range(60):
        close = 100 + ((idx % 10) - 5) * 0.6
        rows.append(
            {
                "bar_date": start + timedelta(days=idx),
                "open": close - 0.2,
                "high": close + 1.0,
                "low": close - 1.0,
                "close": close,
                "volume": 2_000_000 + idx * 10_000,
            }
        )
    frame = pd.DataFrame(rows)

    result = service.build_indicator_frame(frame)

    for column in [
        "sma_20",
        "atr_14",
        "adx_14",
        "rsi_14",
        "normalized_sma_20_slope",
        "net_drift_30",
        "avg_dollar_volume_20",
    ]:
        assert column in result.columns
    assert result["atr_14"].dropna().iloc[-1] > 0
