from __future__ import annotations

from datetime import date, datetime, timedelta

import pandas as pd

from app.config.settings import Settings
from app.models import Indicator
from app.services.range_detection_service import RangeDetectionService


def test_range_detection_qualifies_sideways_data() -> None:
    settings = Settings()
    service = RangeDetectionService(settings)
    start = date(2026, 1, 1)
    rows = []
    closes = [100, 101, 102, 101, 100, 99, 98, 99, 100, 101] * 3
    for idx, close in enumerate(closes):
        rows.append(
            {
                "bar_date": start + timedelta(days=idx),
                "open": close - 0.3,
                "high": close + 1.1,
                "low": close - 1.1,
                "close": close,
            }
        )
    frame = pd.DataFrame(rows)
    indicator = Indicator(
        stock_id=1,
        timeframe="1d",
        bar_date=rows[-1]["bar_date"],
        sma_20=100.0,
        sma_20_slope=0.02,
        normalized_sma_20_slope=0.04,
        atr_14=1.8,
        adx_14=15.0,
        rsi_14=48.0,
        net_drift_30=0.5,
        avg_volume_20=4_000_000,
        avg_dollar_volume_20=250_000_000,
        computed_at=datetime.utcnow(),
    )

    result = service.analyze_frame(frame, indicator)

    assert result.qualifies is True
    assert result.touch_count_support >= 2
    assert result.touch_count_resistance >= 2
    assert result.containment_ratio >= 0.9
