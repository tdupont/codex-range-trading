from __future__ import annotations

from datetime import date, datetime

from app.config.settings import Settings
from app.models import Indicator, OHLCV, RangeSnapshot
from app.services.scoring_service import ScoringService
from app.services.setup_service import SetupService


def _build_range_snapshot() -> RangeSnapshot:
    return RangeSnapshot(
        stock_id=1,
        timeframe="1d",
        scan_date=date(2026, 3, 18),
        lookback_bars=30,
        upper_bound=110.0,
        lower_bound=100.0,
        support_zone_low=100.0,
        support_zone_high=100.6,
        resistance_zone_low=109.4,
        resistance_zone_high=110.0,
        midline=105.0,
        range_width=10.0,
        atr_14=2.0,
        latest_close=100.4,
        touch_count_support=3,
        touch_count_resistance=3,
        containment_ratio=0.96,
        drift_to_range_ratio=0.08,
        has_recent_breakout=False,
        qualifies=True,
        rejection_reason=None,
        computed_from_bar_date=date(2026, 3, 18),
        created_at=datetime.utcnow(),
    )


def test_scoring_service_returns_0_to_100_scores() -> None:
    score = ScoringService().score_range(
        _build_range_snapshot(),
        Indicator(
            stock_id=1,
            timeframe="1d",
            bar_date=date(2026, 3, 18),
            adx_14=12.0,
            sma_20=101.0,
            sma_20_slope=0.01,
            normalized_sma_20_slope=0.03,
            atr_14=2.0,
            rsi_14=35.0,
            net_drift_30=0.8,
            avg_volume_20=4_000_000,
            avg_dollar_volume_20=350_000_000,
            computed_at=datetime.utcnow(),
        ),
    )

    assert 0 <= score.range_score <= 100
    assert 0 <= score.range_validity_score <= 100
    assert 0 <= score.tradeability_score <= 100
    assert 0 <= score.opportunity_score <= 100


def test_setup_service_creates_active_long_setup() -> None:
    service = SetupService(Settings())
    setups = service.build_setups(
        _build_range_snapshot(),
        Indicator(
            stock_id=1,
            timeframe="1d",
            bar_date=date(2026, 3, 18),
            adx_14=12.0,
            sma_20=101.0,
            sma_20_slope=0.01,
            normalized_sma_20_slope=0.03,
            atr_14=2.0,
            rsi_14=35.0,
            net_drift_30=0.8,
            avg_volume_20=4_000_000,
            avg_dollar_volume_20=350_000_000,
            computed_at=datetime.utcnow(),
        ),
        OHLCV(
            stock_id=1,
            timeframe="1d",
            bar_date=date(2026, 3, 18),
            open=100.1,
            high=101.0,
            low=99.1,
            close=100.5,
            adjusted_close=100.5,
            volume=4_000_000,
            provider="test",
            provider_timezone="America/New_York",
            is_complete=True,
            ingested_at=datetime.utcnow(),
        ),
    )

    long_setup = next(setup for setup in setups if setup.setup_direction == "long")
    assert long_setup.setup_status == "active"
    assert long_setup.stop_price < long_setup.entry_low
