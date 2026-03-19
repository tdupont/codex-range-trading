# API Specification

## Overview

The API serves the latest persisted range scan results for the Range Trading Screener MVP. It is read-heavy and focused on simple filtering, ranking, and detail retrieval.

Base path suggestion:

`/api/v1`

Common response conventions:

- JSON only
- UTC timestamps in ISO 8601 format
- pagination metadata on collection endpoints
- explicit `as_of_date` fields for market-derived data

## Error shape

All non-2xx responses should follow this shape:

```json
{
  "error": {
    "code": "not_found",
    "message": "Ticker not found",
    "details": {
      "ticker": "XXXX"
    }
  }
}
```

Suggested error codes:

- `bad_request`
- `not_found`
- `conflict`
- `unprocessable_entity`
- `internal_error`
- `service_unavailable`

## Pagination and filtering conventions

Collection endpoints should support:

- `page` default `1`
- `page_size` default `25`, max `100`
- `sort_by`
- `sort_order` as `asc` or `desc`

Filtering ideas for MVP:

- `ticker`
- `min_score`
- `min_range_validity_score`
- `min_tradeability_score`
- `min_opportunity_score`
- `direction` with values `long`, `short`, `any`
- `has_active_setup`
- `min_avg_dollar_volume`
- `as_of_date`

Collection response envelope:

```json
{
  "data": [],
  "pagination": {
    "page": 1,
    "page_size": 25,
    "total_items": 132,
    "total_pages": 6
  }
}
```

## GET /health

Simple liveness/readiness endpoint for local development and deployment checks.

### Example response

```json
{
  "status": "ok",
  "service": "range-trading-screener-api",
  "version": "0.1.0"
}
```

## GET /ranges

Returns the latest qualified range-bound stocks, ranked and filterable.

### Query params

- `page`
- `page_size`
- `sort_by` such as `range_score`, `opportunity_score`, `ticker`
- `sort_order`
- `min_score`
- `direction`
- `has_active_setup`
- `as_of_date`

### Example request

`GET /api/v1/ranges?page=1&page_size=25&sort_by=range_score&sort_order=desc&min_score=70`

### Example response

```json
{
  "data": [
    {
      "ticker": "AAPL",
      "name": "Apple Inc.",
      "as_of_date": "2026-03-10",
      "range_score": 82.4,
      "range_validity_score": 84.0,
      "tradeability_score": 78.2,
      "opportunity_score": 76.5,
      "upper_bound": 214.8,
      "lower_bound": 198.2,
      "midline": 206.5,
      "support_zone": {
        "low": 198.2,
        "high": 199.4
      },
      "resistance_zone": {
        "low": 213.6,
        "high": 214.8
      },
      "touch_counts": {
        "support": 3,
        "resistance": 2
      },
      "containment_ratio": 0.93,
      "atr_14": 4.1,
      "adx_14": 16.8,
      "latest_close": 199.1,
      "active_setup": {
        "direction": "long",
        "entry_zone_low": 198.2,
        "entry_zone_high": 199.4,
        "stop_price": 196.15,
        "target_1": 206.5,
        "target_2": 214.8
      }
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 25,
    "total_items": 1,
    "total_pages": 1
  }
}
```

## GET /ranges/{ticker}

Returns the latest range detail for a single ticker, including score breakdown, setup information, and recent candles needed by the chart.

### Path params

- `ticker`: uppercase stock symbol

### Example request

`GET /api/v1/ranges/AAPL`

### Example response

```json
{
  "ticker": "AAPL",
  "name": "Apple Inc.",
  "as_of_date": "2026-03-10",
  "latest_close": 199.1,
  "range": {
    "qualified": true,
    "lookback_days": 30,
    "upper_bound": 214.8,
    "lower_bound": 198.2,
    "midline": 206.5,
    "width": 16.6,
    "width_atr_multiple": 4.05,
    "support_zone": {
      "low": 198.2,
      "high": 199.4
    },
    "resistance_zone": {
      "low": 213.6,
      "high": 214.8
    },
    "touch_counts": {
      "support": 3,
      "resistance": 2
    },
    "containment_ratio": 0.93
  },
  "indicators": {
    "adx_14": 16.8,
    "atr_14": 4.1,
    "rsi_14": 37.2,
    "sma_20": 205.7,
    "sma_20_slope": 0.08
  },
  "scores": {
    "range_score": 82.4,
    "range_validity_score": 84.0,
    "tradeability_score": 78.2,
    "opportunity_score": 76.5,
    "components": {
      "touch_quality": 27.0,
      "trend_weakness": 16.0,
      "containment_quality": 13.5,
      "range_width": 12.5,
      "liquidity": 7.0,
      "current_opportunity_location": 6.4
    }
  },
  "setup": {
    "direction": "long",
    "status": "active",
    "entry_zone_low": 198.2,
    "entry_zone_high": 199.4,
    "stop_price": 196.15,
    "target_1": 206.5,
    "target_2": 214.8,
    "rejection_signal": "bullish_rejection"
  },
  "recent_candles": [
    {
      "date": "2026-03-06",
      "open": 201.2,
      "high": 202.5,
      "low": 198.4,
      "close": 199.7,
      "volume": 55123400
    }
  ]
}
```

## GET /opportunities

Returns only active long and short setups.

### Query params

- `page`
- `page_size`
- `direction`
- `min_opportunity_score`
- `as_of_date`

### Example request

`GET /api/v1/opportunities?direction=long&min_opportunity_score=70`

### Example response

```json
{
  "data": [
    {
      "ticker": "AAPL",
      "as_of_date": "2026-03-10",
      "direction": "long",
      "opportunity_score": 76.5,
      "latest_close": 199.1,
      "entry_zone_low": 198.2,
      "entry_zone_high": 199.4,
      "stop_price": 196.15,
      "target_1": 206.5,
      "target_2": 214.8
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 25,
    "total_items": 1,
    "total_pages": 1
  }
}
```

## GET /alerts

Returns the latest persisted alert events. For MVP, an alert is a stored event created when a ticker newly enters an active setup state or crosses a configured score threshold.

### Query params

- `page`
- `page_size`
- `ticker`
- `alert_type`
- `direction`
- `unread_only` if user state is later added

### Example response

```json
{
  "data": [
    {
      "id": 101,
      "ticker": "AAPL",
      "created_at": "2026-03-10T20:05:00Z",
      "alert_type": "new_opportunity",
      "direction": "long",
      "message": "AAPL entered support zone with active long setup.",
      "related_range_score": 82.4
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 25,
    "total_items": 1,
    "total_pages": 1
  }
}
```

## Notes on future auth

Authentication is not required for the MVP if the app is single-user or internal. If auth is added later:

- use token-based API auth or session auth at the frontend boundary
- keep market scan data read-only for most users
- reserve manual scan triggers and config changes for privileged users
- design alerts so user-specific read state can be added without rewriting the core alert event model
