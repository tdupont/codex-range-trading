# Database Schema

## Storage Strategy

SQLite is the default MVP database. The schema should stay conservative and relational so that PostgreSQL migration later is straightforward.

General design rules:

- use integer surrogate keys for MVP simplicity
- enforce uniqueness on natural business keys where appropriate
- store `timeframe` explicitly on time-series and scan-derived tables
- keep provider metadata and timestamps for traceability
- separate raw bars, indicators, ranges, scores, and setups

## Tables

### `stocks`

Purpose: canonical S&P 500 security master for the app universe.

Columns:

- `id` INTEGER PRIMARY KEY
- `ticker` TEXT NOT NULL UNIQUE
- `name` TEXT NOT NULL
- `sector` TEXT NULL
- `industry` TEXT NULL
- `exchange` TEXT NULL
- `is_active` BOOLEAN NOT NULL DEFAULT 1
- `universe_source` TEXT NULL
- `created_at` TIMESTAMP NOT NULL
- `updated_at` TIMESTAMP NOT NULL

Indexes:

- unique index on `ticker`
- index on `is_active`

### `ohlcv`

Purpose: completed historical market bars used for analytics.

Columns:

- `id` INTEGER PRIMARY KEY
- `stock_id` INTEGER NOT NULL
- `timeframe` TEXT NOT NULL
- `bar_date` DATE NOT NULL
- `open` REAL NOT NULL
- `high` REAL NOT NULL
- `low` REAL NOT NULL
- `close` REAL NOT NULL
- `adjusted_close` REAL NULL
- `volume` REAL NOT NULL
- `provider` TEXT NOT NULL
- `provider_timezone` TEXT NULL
- `is_complete` BOOLEAN NOT NULL DEFAULT 1
- `ingested_at` TIMESTAMP NOT NULL

Keys and indexes:

- foreign key `stock_id -> stocks.id`
- unique index on (`stock_id`, `timeframe`, `bar_date`)
- index on (`timeframe`, `bar_date`)

Notes:

- Only completed candles should be stored with `is_complete = 1` for MVP analytics.
- If future ingestion stages ever capture incomplete bars, they must never be used by the analytics pipeline.

### `indicators`

Purpose: persisted indicator snapshots for a specific symbol, timeframe, and bar date.

Columns:

- `id` INTEGER PRIMARY KEY
- `stock_id` INTEGER NOT NULL
- `timeframe` TEXT NOT NULL
- `bar_date` DATE NOT NULL
- `adx_14` REAL NULL
- `sma_20` REAL NULL
- `sma_20_slope` REAL NULL
- `normalized_sma_20_slope` REAL NULL
- `atr_14` REAL NULL
- `rsi_14` REAL NULL
- `net_drift_30` REAL NULL
- `avg_volume_20` REAL NULL
- `avg_dollar_volume_20` REAL NULL
- `computed_at` TIMESTAMP NOT NULL

Keys and indexes:

- foreign key `stock_id -> stocks.id`
- unique index on (`stock_id`, `timeframe`, `bar_date`)

### `ranges`

Purpose: persisted range detection outputs for the latest completed scan state of a symbol.

Columns:

- `id` INTEGER PRIMARY KEY
- `stock_id` INTEGER NOT NULL
- `timeframe` TEXT NOT NULL
- `scan_date` DATE NOT NULL
- `lookback_bars` INTEGER NOT NULL
- `upper_bound` REAL NOT NULL
- `lower_bound` REAL NOT NULL
- `support_zone_low` REAL NOT NULL
- `support_zone_high` REAL NOT NULL
- `resistance_zone_low` REAL NOT NULL
- `resistance_zone_high` REAL NOT NULL
- `midline` REAL NOT NULL
- `range_width` REAL NOT NULL
- `atr_14` REAL NOT NULL
- `touch_count_support` INTEGER NOT NULL
- `touch_count_resistance` INTEGER NOT NULL
- `containment_ratio` REAL NOT NULL
- `drift_to_range_ratio` REAL NOT NULL
- `has_recent_breakout` BOOLEAN NOT NULL
- `qualifies` BOOLEAN NOT NULL
- `rejection_reason` TEXT NULL
- `computed_from_bar_date` DATE NOT NULL
- `created_at` TIMESTAMP NOT NULL

Keys and indexes:

- foreign key `stock_id -> stocks.id`
- unique index on (`stock_id`, `timeframe`, `scan_date`)
- index on (`timeframe`, `scan_date`, `qualifies`)

Notes:

- MVP may choose to store only qualifying rows initially.
- Keeping `qualifies` and `rejection_reason` allows later debugging without redesign.

### `range_scores`

Purpose: explainable scoring outputs tied to a range record.

Columns:

- `id` INTEGER PRIMARY KEY
- `range_id` INTEGER NOT NULL
- `range_score` REAL NOT NULL
- `range_validity_score` REAL NOT NULL
- `tradeability_score` REAL NOT NULL
- `opportunity_score` REAL NOT NULL
- `touch_quality_score` REAL NOT NULL
- `trend_weakness_score` REAL NOT NULL
- `containment_quality_score` REAL NOT NULL
- `width_vs_atr_score` REAL NOT NULL
- `liquidity_score` REAL NOT NULL
- `opportunity_location_score` REAL NOT NULL
- `scored_at` TIMESTAMP NOT NULL

Keys and indexes:

- foreign key `range_id -> ranges.id`
- unique index on `range_id`
- index on `range_score`

### `trade_setups`

Purpose: long and short setup candidates generated from a qualified range.

Columns:

- `id` INTEGER PRIMARY KEY
- `range_id` INTEGER NOT NULL
- `setup_direction` TEXT NOT NULL
- `setup_status` TEXT NOT NULL
- `trigger_bar_date` DATE NOT NULL
- `entry_low` REAL NOT NULL
- `entry_high` REAL NOT NULL
- `stop_price` REAL NOT NULL
- `target_1_price` REAL NOT NULL
- `target_2_price` REAL NOT NULL
- `rsi_14` REAL NULL
- `rejection_signal` TEXT NULL
- `notes` TEXT NULL
- `created_at` TIMESTAMP NOT NULL
- `updated_at` TIMESTAMP NOT NULL

Keys and indexes:

- foreign key `range_id -> ranges.id`
- index on (`setup_direction`, `setup_status`)
- index on `trigger_bar_date`

Notes:

- `setup_status` can start with values like `candidate`, `active`, or `invalidated`.
- A symbol can have both long and short setup records over time, but only one per direction per scan snapshot should be current.

### `alerts`

Purpose: placeholder table for future change notifications and watchlist events.

Columns:

- `id` INTEGER PRIMARY KEY
- `stock_id` INTEGER NOT NULL
- `range_id` INTEGER NULL
- `trade_setup_id` INTEGER NULL
- `alert_type` TEXT NOT NULL
- `alert_status` TEXT NOT NULL
- `message` TEXT NULL
- `triggered_at` TIMESTAMP NOT NULL
- `acknowledged_at` TIMESTAMP NULL

Keys and indexes:

- foreign key `stock_id -> stocks.id`
- foreign key `range_id -> ranges.id`
- foreign key `trade_setup_id -> trade_setups.id`
- index on (`alert_type`, `alert_status`)
- index on `triggered_at`

Notes:

- This table is included now to preserve room for future work, but alerts are not core MVP functionality.

## Relationships

- one `stocks` row has many `ohlcv` rows
- one `stocks` row has many `indicators` rows
- one `stocks` row has many `ranges` rows
- one `ranges` row has one `range_scores` row
- one `ranges` row has many `trade_setups` rows over time
- one `stocks` row may have many `alerts`

## Scan Metadata Recommendation

The MVP can optionally add a later `scan_runs` table to track each orchestration run. It is not required for the first schema pass but is recommended once scans become operational.

## SQLite MVP Notes

- Use ISO date strings or timezone-aware timestamps consistently.
- Prefer explicit transactions for scan steps.
- Avoid SQLite-specific SQL in higher-level query code when portability matters.
- Store booleans using SQLite-compatible integer semantics through the ORM.

## PostgreSQL Migration Notes

- Preserve explicit indexes and unique constraints so they translate cleanly.
- Keep text enums modeled as constrained strings first; PostgreSQL enums can be added later if useful.
- Avoid implicit SQLite-only behavior such as relying on weak typing in business logic.
