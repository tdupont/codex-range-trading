from decimal import Decimal

from app.core.settings import Settings
from app.models import Indicator, RangeSnapshot
from app.services.scoring_service import ScoringService


def test_scoring_returns_weighted_scores_between_zero_and_hundred() -> None:
    service = ScoringService(Settings())
    snapshot = RangeSnapshot(
        stock_id=1,
        as_of_date=None,
        lookback_days=30,
        upper_bound=Decimal("110.000000"),
        lower_bound=Decimal("100.000000"),
        midline=Decimal("105.000000"),
        range_width=Decimal("10.000000"),
        range_width_atr_multiple=Decimal("3.500000"),
        support_zone_low=Decimal("100.000000"),
        support_zone_high=Decimal("100.500000"),
        resistance_zone_low=Decimal("109.500000"),
        resistance_zone_high=Decimal("110.000000"),
        containment_ratio=Decimal("0.930000"),
        support_touch_count=3,
        resistance_touch_count=2,
        latest_close=Decimal("100.250000"),
        qualified=True,
        notes_json={},
    )
    indicator = Indicator(
        stock_id=1,
        trade_date=None,
        sma_20=Decimal("105.000000"),
        sma_20_slope=Decimal("0.030000"),
        atr_14=Decimal("2.800000"),
        adx_14=Decimal("14.000000"),
        rsi_14=Decimal("38.000000"),
        avg_dollar_volume_20=Decimal("60000000.00"),
    )

    score = service.score(snapshot, indicator)

    assert 0 <= score.range_score <= 100
    assert 0 <= score.range_validity_score <= 100
    assert 0 <= score.tradeability_score <= 100
    assert 0 <= score.opportunity_score <= 100
    assert round(
        score.touch_quality
        + score.trend_weakness
        + score.containment_quality
        + score.range_width
        + score.liquidity
        + score.current_opportunity_location,
        2,
    ) == score.range_score
