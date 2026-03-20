from datetime import date, timedelta
from decimal import Decimal

import pandas as pd

from app.core.settings import Settings
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
                "trade_date": start + timedelta(days=idx),
                "open": close - 0.4,
                "high": close + 1,
                "low": close - 1,
                "close": close,
            }
        )
    frame = pd.DataFrame(rows)
    indicator = Indicator(
        stock_id=1,
        trade_date=rows[-1]["trade_date"],
        sma_20=Decimal("100.000000"),
        sma_20_slope=Decimal("0.020000"),
        atr_14=Decimal("1.800000"),
        adx_14=Decimal("15.000000"),
        rsi_14=Decimal("48.000000"),
        avg_dollar_volume_20=Decimal("25000000.00"),
    )

    result = service.analyze_frame(frame, indicator)

    assert result.qualified is True
    assert result.support_touch_count >= 2
    assert result.resistance_touch_count >= 2
    assert result.containment_ratio >= 0.9
