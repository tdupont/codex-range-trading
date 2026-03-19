# Database Schema

## Overview

PostgreSQL is the system of record for market data, derived analytics, scan outputs, and alert events. The MVP favors explicit tables and daily snapshots over highly compressed storage so that scans are debuggable and API reads stay simple.

All market-derived rows should be tied to both a `stock_id` and a `trade_date` or `as_of_date`.

## Relationship summary

- `stocks` is the parent entity for all ticker-specific tables.
- `ohlcv` stores normalized daily candles.
- `indicators` stores daily technical indicators derived from `ohlcv`.
- `ranges` stores qualifying range snapshots for a given date.
- `range_scores` stores component and composite scores for a `ranges` row.
- `trade_setups` stores generated long or short setup rows tied to a `ranges` row.
- `alerts` stores event records tied to a ticker and optionally a setup/range snapshot.

## Table: `stocks`

Canonical ticker and universe membership table.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `bigserial` | Primary key |
| `ticker` | `varchar(16)` | Unique uppercase symbol |
| `name` | `varchar(255)` | Company name |
| `exchange` | `varchar(32)` | Optional exchange code |
| `sector` | `varchar(128)` | Optional metadata |
| `industry` | `varchar(128)` | Optional metadata |
| `is_active` | `boolean` | True when currently in tracked universe |
| `universe` | `varchar(32)` | For MVP expected value is `sp500` |
| `source` | `varchar(64)` | Universe source identifier |
| `created_at` | `timestamptz` | Row creation time |
| `updated_at` | `timestamptz` | Row update time |

Indexes and constraints:

- primary key on `id`
- unique index on `ticker`
- index on `(universe, is_active)`

## Table: `ohlcv`

Normalized daily candle history.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `bigserial` | Primary key |
| `stock_id` | `bigint` | FK to `stocks.id` |
| `trade_date` | `date` | Trading session date |
| `open` | `numeric(18,6)` | Daily open |
| `high` | `numeric(18,6)` | Daily high |
| `low` | `numeric(18,6)` | Daily low |
| `close` | `numeric(18,6)` | Daily close |
| `adjusted_close` | `numeric(18,6)` | Optional provider-adjusted close |
| `volume` | `bigint` | Daily share volume |
| `vwap` | `numeric(18,6)` | Optional if provider supplies it |
| `data_source` | `varchar(64)` | Provider identifier |
| `is_adjusted_series` | `boolean` | Whether OHLC values are adjusted |
| `ingested_at` | `timestamptz` | Ingestion timestamp |
| `created_at` | `timestamptz` | Row creation time |

Indexes and constraints:

- unique index on `(stock_id, trade_date)`
- index on `(trade_date)`
- index on `(stock_id, trade_date desc)`

## Table: `indicators`

Daily derived indicator snapshots.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `bigserial` | Primary key |
| `stock_id` | `bigint` | FK to `stocks.id` |
| `trade_date` | `date` | Same date as driving candle |
| `sma_20` | `numeric(18,6)` | 20-day simple moving average |
| `sma_20_slope` | `numeric(18,6)` | Absolute/normalized slope metric |
| `atr_14` | `numeric(18,6)` | 14-day average true range |
| `adx_14` | `numeric(18,6)` | 14-day ADX |
| `rsi_14` | `numeric(18,6)` | 14-day RSI |
| `avg_dollar_volume_20` | `numeric(18,2)` | Liquidity proxy |
| `created_at` | `timestamptz` | Row creation time |

Indexes and constraints:

- unique index on `(stock_id, trade_date)`
- index on `(trade_date)`
- index on `(stock_id, trade_date desc)`

## Table: `ranges`

One row per ticker per scan date when the ticker qualifies as range-bound in the MVP.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `bigserial` | Primary key |
| `stock_id` | `bigint` | FK to `stocks.id` |
| `as_of_date` | `date` | Scan/result date |
| `lookback_days` | `integer` | MVP default `30` |
| `upper_bound` | `numeric(18,6)` | Highest high over lookback |
| `lower_bound` | `numeric(18,6)` | Lowest low over lookback |
| `midline` | `numeric(18,6)` | Midpoint of range |
| `range_width` | `numeric(18,6)` | `upper_bound - lower_bound` |
| `range_width_atr_multiple` | `numeric(18,6)` | Width divided by ATR |
| `support_zone_low` | `numeric(18,6)` | Lower support zone bound |
| `support_zone_high` | `numeric(18,6)` | Upper support zone bound |
| `resistance_zone_low` | `numeric(18,6)` | Lower resistance zone bound |
| `resistance_zone_high` | `numeric(18,6)` | Upper resistance zone bound |
| `containment_ratio` | `numeric(8,6)` | Fraction of closes inside bounds |
| `support_touch_count` | `integer` | Qualified touch count |
| `resistance_touch_count` | `integer` | Qualified touch count |
| `latest_close` | `numeric(18,6)` | Close on `as_of_date` |
| `qualified` | `boolean` | True for persisted MVP rows; included for extensibility |
| `notes_json` | `jsonb` | Optional debug metadata |
| `created_at` | `timestamptz` | Row creation time |

Indexes and constraints:

- unique index on `(stock_id, as_of_date)`
- index on `(as_of_date desc)`
- index on `(qualified, as_of_date desc)`

## Table: `range_scores`

Stores the final and component scores for a range snapshot.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `bigserial` | Primary key |
| `range_id` | `bigint` | FK to `ranges.id` |
| `range_score` | `numeric(6,2)` | 0 to 100 composite score |
| `range_validity_score` | `numeric(6,2)` | 0 to 100 |
| `tradeability_score` | `numeric(6,2)` | 0 to 100 |
| `opportunity_score` | `numeric(6,2)` | 0 to 100 |
| `touch_quality_score` | `numeric(6,2)` | Weighted component |
| `trend_weakness_score` | `numeric(6,2)` | Weighted component |
| `containment_quality_score` | `numeric(6,2)` | Weighted component |
| `range_width_score` | `numeric(6,2)` | Weighted component |
| `liquidity_score` | `numeric(6,2)` | Weighted component |
| `current_opportunity_location_score` | `numeric(6,2)` | Weighted component |
| `scoring_version` | `varchar(32)` | For future rule evolution |
| `created_at` | `timestamptz` | Row creation time |

Indexes and constraints:

- unique index on `range_id`
- index on `(range_score desc)`
- index on `(opportunity_score desc)`

## Table: `trade_setups`

Directional trade ideas generated from a range snapshot.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `bigserial` | Primary key |
| `range_id` | `bigint` | FK to `ranges.id` |
| `stock_id` | `bigint` | FK to `stocks.id` for direct lookup |
| `as_of_date` | `date` | Setup date |
| `direction` | `varchar(8)` | `long` or `short` |
| `status` | `varchar(16)` | `active`, `inactive`, `expired` |
| `entry_zone_low` | `numeric(18,6)` | Entry zone low |
| `entry_zone_high` | `numeric(18,6)` | Entry zone high |
| `stop_price` | `numeric(18,6)` | ATR-buffered stop |
| `target_1_price` | `numeric(18,6)` | Midline |
| `target_2_price` | `numeric(18,6)` | Opposite range side |
| `rejection_signal` | `varchar(64)` | `bullish_rejection` or `bearish_rejection` |
| `latest_close` | `numeric(18,6)` | Current close at setup time |
| `created_at` | `timestamptz` | Row creation time |

Indexes and constraints:

- unique index on `(range_id, direction)`
- index on `(as_of_date desc, status)`
- index on `(stock_id, as_of_date desc)`

## Table: `alerts`

Persisted events when setup state changes or thresholds are crossed.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `bigserial` | Primary key |
| `stock_id` | `bigint` | FK to `stocks.id` |
| `range_id` | `bigint` | Nullable FK to `ranges.id` |
| `trade_setup_id` | `bigint` | Nullable FK to `trade_setups.id` |
| `alert_type` | `varchar(32)` | e.g. `new_opportunity` |
| `direction` | `varchar(8)` | Nullable long/short |
| `message` | `text` | Human-readable summary |
| `payload_json` | `jsonb` | Optional structured payload |
| `created_at` | `timestamptz` | Event time |

Indexes and constraints:

- index on `(created_at desc)`
- index on `(stock_id, created_at desc)`
- index on `(alert_type, created_at desc)`

## Key relationships

- `ohlcv.stock_id -> stocks.id`
- `indicators.stock_id -> stocks.id`
- `ranges.stock_id -> stocks.id`
- `range_scores.range_id -> ranges.id`
- `trade_setups.range_id -> ranges.id`
- `trade_setups.stock_id -> stocks.id`
- `alerts.stock_id -> stocks.id`
- `alerts.range_id -> ranges.id`
- `alerts.trade_setup_id -> trade_setups.id`

## Notes on time-series retention

- MVP recommendation: keep all daily OHLCV and indicator history used for analysis rather than pruning aggressively.
- Minimum practical retention target: two years of daily bars and indicators per ticker.
- Range, score, setup, and alert snapshots should be retained indefinitely during MVP so changes in logic and outcomes can be audited.
- If storage becomes a concern later, archive older OHLCV and indicator partitions before deleting them.
- Partitioning by year or by trade date range can be added later, but is not required for the first implementation.

## Implementation notes

- Numeric precision should be consistent across all price fields to avoid chart and API rounding mismatches.
- Use UTC timestamps for metadata columns even though market dates are stored as `date`.
- Avoid storing arrays of candles inside snapshot tables; keep chart data sourced from `ohlcv`.
