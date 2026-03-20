from __future__ import annotations

from math import ceil

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy import Select, desc, func, select
from sqlalchemy.orm import Session, aliased

from app.api.deps import get_db
from app.core.constants import SETUP_STATUS_ACTIVE
from app.core.settings import get_settings
from app.models import Alert, Indicator, OHLCV, RangeScore, RangeSnapshot, Stock, TradeSetup
from app.schemas import (
    AlertListItem,
    HealthResponse,
    OpportunityListItem,
    PaginatedResponse,
    Pagination,
    RangeDetailResponse,
    RangeListItem,
)
from app.schemas.range import CandlePayload, IndicatorPayload, PriceZone, RangePayload, ScoreComponents, ScorePayload, SetupSummary, TouchCounts

router = APIRouter(prefix=get_settings().api_prefix)
settings = get_settings()


@router.get("/health", tags=["health"], response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="range-trading-screener-api", version="0.1.0")


@router.get("/ranges", tags=["ranges"], response_model=PaginatedResponse[RangeListItem])
def get_ranges(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    sort_by: str = Query(default="range_score"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    min_score: float | None = Query(default=None),
    near_support: bool = Query(default=False),
    near_resistance: bool = Query(default=False),
    direction: str = Query(default="any"),
    limit: int | None = Query(default=None, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedResponse[RangeListItem]:
    query = _base_range_query()
    if min_score is not None:
        query = query.where(RangeScore.range_score >= min_score)
    if near_support:
        query = query.where(RangeSnapshot.latest_close <= RangeSnapshot.support_zone_high)
    if near_resistance:
        query = query.where(RangeSnapshot.latest_close >= RangeSnapshot.resistance_zone_low)
    sort_column = {
        "ticker": Stock.ticker,
        "opportunity_score": RangeScore.opportunity_score,
        "range_score": RangeScore.range_score,
    }.get(sort_by, RangeScore.range_score)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)

    effective_page_size = min(limit, page_size) if limit else page_size
    rows = db.execute(query).all()
    items = [_serialize_range_list_item(*row) for row in rows]
    if direction in {"long", "short"}:
        items = [
            item for item in items if item.active_setup is not None and item.active_setup.direction == direction
        ]
    total_items = len(items)
    start_idx = (page - 1) * effective_page_size
    items = items[start_idx : start_idx + effective_page_size]
    return PaginatedResponse(
        data=items,
        pagination=Pagination(
            page=page,
            page_size=effective_page_size,
            total_items=total_items,
            total_pages=max(1, ceil(total_items / effective_page_size)) if total_items else 1,
        ),
    )


@router.get("/ranges/{ticker}", tags=["ranges"], response_model=RangeDetailResponse)
def get_range_detail(ticker: str, db: Session = Depends(get_db)) -> RangeDetailResponse:
    row = db.execute(_base_range_query().where(Stock.ticker == ticker.upper())).first()
    if row is None:
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "not_found",
                    "message": "Ticker not found",
                    "details": {"ticker": ticker},
                }
            },
        )
    stock, snapshot, score, indicator, setup = row
    candles = list(
        db.scalars(
            select(OHLCV)
            .where(OHLCV.stock_id == stock.id)
            .order_by(OHLCV.trade_date.desc())
            .limit(60)
        )
    )
    active_setup = setup if setup and setup.status == SETUP_STATUS_ACTIVE else None
    return RangeDetailResponse(
        ticker=stock.ticker,
        name=stock.name,
        as_of_date=snapshot.as_of_date,
        latest_close=snapshot.latest_close,
        range=RangePayload(
            qualified=snapshot.qualified,
            lookback_days=snapshot.lookback_days,
            upper_bound=snapshot.upper_bound,
            lower_bound=snapshot.lower_bound,
            midline=snapshot.midline,
            width=snapshot.range_width,
            width_atr_multiple=snapshot.range_width_atr_multiple,
            support_zone=PriceZone(low=snapshot.support_zone_low, high=snapshot.support_zone_high),
            resistance_zone=PriceZone(low=snapshot.resistance_zone_low, high=snapshot.resistance_zone_high),
            touch_counts=TouchCounts(
                support=snapshot.support_touch_count,
                resistance=snapshot.resistance_touch_count,
            ),
            containment_ratio=snapshot.containment_ratio,
        ),
        indicators=IndicatorPayload(
            adx_14=indicator.adx_14,
            atr_14=indicator.atr_14,
            rsi_14=indicator.rsi_14,
            sma_20=indicator.sma_20,
            sma_20_slope=indicator.sma_20_slope,
            avg_dollar_volume_20=indicator.avg_dollar_volume_20,
        ),
        scores=ScorePayload(
            range_score=score.range_score,
            range_validity_score=score.range_validity_score,
            tradeability_score=score.tradeability_score,
            opportunity_score=score.opportunity_score,
            components=ScoreComponents(
                touch_quality=score.touch_quality_score,
                trend_weakness=score.trend_weakness_score,
                containment_quality=score.containment_quality_score,
                range_width=score.range_width_score,
                liquidity=score.liquidity_score,
                current_opportunity_location=score.current_opportunity_location_score,
            ),
        ),
        setup=_serialize_setup(active_setup) if active_setup else None,
        recent_candles=[
            CandlePayload(
                date=candle.trade_date,
                open=candle.open,
                high=candle.high,
                low=candle.low,
                close=candle.close,
                volume=candle.volume,
            )
            for candle in reversed(candles)
        ],
    )


@router.get("/opportunities", tags=["opportunities"], response_model=PaginatedResponse[OpportunityListItem])
def get_opportunities(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    direction: str = Query(default="any"),
    min_opportunity_score: float | None = Query(default=None),
    db: Session = Depends(get_db),
) -> PaginatedResponse[OpportunityListItem]:
    query = (
        select(Stock, TradeSetup, RangeScore)
        .join(TradeSetup, TradeSetup.stock_id == Stock.id)
        .join(RangeScore, RangeScore.range_id == TradeSetup.range_id)
        .where(TradeSetup.status == SETUP_STATUS_ACTIVE)
    )
    if direction in {"long", "short"}:
        query = query.where(TradeSetup.direction == direction)
    if min_opportunity_score is not None:
        query = query.where(RangeScore.opportunity_score >= min_opportunity_score)
    total_items = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = db.execute(query.order_by(desc(RangeScore.opportunity_score)).offset((page - 1) * page_size).limit(page_size)).all()
    items = [
        OpportunityListItem(
            ticker=stock.ticker,
            as_of_date=setup.as_of_date,
            direction=setup.direction,
            opportunity_score=score.opportunity_score,
            latest_close=setup.latest_close,
            entry_zone_low=setup.entry_zone_low,
            entry_zone_high=setup.entry_zone_high,
            stop_price=setup.stop_price,
            target_1=setup.target_1_price,
            target_2=setup.target_2_price,
        )
        for stock, setup, score in rows
    ]
    return PaginatedResponse(
        data=items,
        pagination=Pagination(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=max(1, ceil(total_items / page_size)) if total_items else 1,
        ),
    )


@router.get("/alerts", tags=["alerts"], response_model=PaginatedResponse[AlertListItem])
def get_alerts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    ticker: str | None = Query(default=None),
    alert_type: str | None = Query(default=None),
    direction: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> PaginatedResponse[AlertListItem]:
    query = select(Alert, Stock, RangeScore).join(Stock, Stock.id == Alert.stock_id).outerjoin(RangeScore, RangeScore.range_id == Alert.range_id)
    if ticker:
        query = query.where(Stock.ticker == ticker.upper())
    if alert_type:
        query = query.where(Alert.alert_type == alert_type)
    if direction:
        query = query.where(Alert.direction == direction)
    total_items = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = db.execute(query.order_by(desc(Alert.created_at)).offset((page - 1) * page_size).limit(page_size)).all()
    items = [
        AlertListItem(
            id=alert.id,
            ticker=stock.ticker,
            created_at=alert.created_at,
            alert_type=alert.alert_type,
            direction=alert.direction,
            message=alert.message,
            related_range_score=score.range_score if score else None,
        )
        for alert, stock, score in rows
    ]
    return PaginatedResponse(
        data=items,
        pagination=Pagination(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=max(1, ceil(total_items / page_size)) if total_items else 1,
        ),
    )


def _base_range_query() -> Select:
    active_setup = aliased(TradeSetup)
    return (
        select(Stock, RangeSnapshot, RangeScore, Indicator, active_setup)
        .join(RangeSnapshot, RangeSnapshot.stock_id == Stock.id)
        .join(RangeScore, RangeScore.range_id == RangeSnapshot.id)
        .join(
            Indicator,
            (Indicator.stock_id == Stock.id) & (Indicator.trade_date == RangeSnapshot.as_of_date),
        )
        .outerjoin(
            active_setup,
            (active_setup.range_id == RangeSnapshot.id)
            & (active_setup.status == SETUP_STATUS_ACTIVE),
        )
    )


def _serialize_range_list_item(
    stock: Stock,
    snapshot: RangeSnapshot,
    score: RangeScore,
    indicator: Indicator,
    setup: TradeSetup | None,
) -> RangeListItem:
    return RangeListItem(
        ticker=stock.ticker,
        name=stock.name,
        as_of_date=snapshot.as_of_date,
        range_score=score.range_score,
        range_validity_score=score.range_validity_score,
        tradeability_score=score.tradeability_score,
        opportunity_score=score.opportunity_score,
        upper_bound=snapshot.upper_bound,
        lower_bound=snapshot.lower_bound,
        midline=snapshot.midline,
        support_zone=PriceZone(low=snapshot.support_zone_low, high=snapshot.support_zone_high),
        resistance_zone=PriceZone(low=snapshot.resistance_zone_low, high=snapshot.resistance_zone_high),
        touch_counts=TouchCounts(
            support=snapshot.support_touch_count,
            resistance=snapshot.resistance_touch_count,
        ),
        containment_ratio=snapshot.containment_ratio,
        atr_14=indicator.atr_14,
        adx_14=indicator.adx_14,
        latest_close=snapshot.latest_close,
        active_setup=_serialize_setup(setup) if setup else None,
    )


def _serialize_setup(setup: TradeSetup) -> SetupSummary:
    return SetupSummary(
        direction=setup.direction,
        status=setup.status,
        entry_zone_low=setup.entry_zone_low,
        entry_zone_high=setup.entry_zone_high,
        stop_price=setup.stop_price,
        target_1=setup.target_1_price,
        target_2=setup.target_2_price,
        rejection_signal=setup.rejection_signal,
    )
