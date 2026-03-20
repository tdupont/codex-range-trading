# Architecture

## High-Level System Architecture

The MVP is a single Python repository centered on a Streamlit app and a local analytics pipeline.

Core runtime pieces:

- Streamlit presentation layer
- analytics and screening services
- data provider adapters
- SQLite persistence
- local scripts for ingestion and scans

The architecture deliberately avoids a mandatory frontend/backend split. If FastAPI is introduced later, it should be an optional extension and not a requirement for the MVP path.

## System Modules

### Streamlit App Modules

- `app/main.py`
  - entry point
  - app shell
  - routing/navigation bootstrap
- `app/pages/`
  - Streamlit page modules such as screener, stock detail, and scan history
- `app/components/`
  - reusable UI blocks such as score cards, filters, data tables, and chart wrappers
- `app/config/`
  - settings loading, thresholds, shared constants

### Analytics And Service Modules

- `app/services/provider_interfaces.py`
  - interfaces for historical bars and live quotes
- `app/services/universe_service.py`
  - S&P 500 seed loading and refresh logic
- `app/services/market_data_service.py`
  - historical bar ingestion and normalization
- `app/services/indicator_service.py`
  - ATR, ADX, SMA, RSI, and derived metrics
- `app/services/range_detection_service.py`
  - qualification rules, bounds, zones, touches, and breakout checks
- `app/services/scoring_service.py`
  - weighted composite scoring and sub-scores
- `app/services/setup_service.py`
  - long and short setup generation
- `app/services/storage_service.py`
  - persistence and query access for SQLite
- `app/services/scan_service.py`
  - orchestration for end-to-end scan runs

### Data And Model Modules

- `app/models/`
  - typed domain models and persistence models
- `app/utils/`
  - date handling, chart helpers, formatting, and common utilities
- `data/seeds/`
  - static input files such as the S&P 500 seed universe
- `data/sample/`
  - sample datasets for development or testing

## Separation Of Concerns

- Streamlit pages should request already-prepared data from services and render it.
- Provider adapters should normalize vendor responses into internal bar and quote models.
- Indicator code should compute metrics, not decide if a stock is tradable.
- Range detection should decide qualification and geometry, not score ranking.
- Scoring should rank candidates and expose explainable component values.
- Setup generation should transform a qualified range into possible trade plans.
- Storage code should persist and retrieve entities but not recalculate business logic.

## Data Flow

### 1. Universe Flow

- Load S&P 500 symbols from a seed source or refresh source.
- Upsert stock metadata into the `stocks` table.
- Preserve status flags rather than deleting history.

### 2. Historical Market Data Flow

- Pull completed OHLCV bars from the `HistoricalMarketDataProvider`.
- Normalize timeframe, timestamps, symbol format, and provider metadata.
- Persist bars into `ohlcv`.

### 3. Indicator Flow

- Read recent bars by symbol and timeframe.
- Compute ADX, SMA, ATR, RSI, normalized slope, drift, and liquidity helpers.
- Persist outputs in `indicators`.

### 4. Range Detection Flow

- Read the latest completed lookback window.
- Compute upper/lower bounds, zones, midline, touch counts, containment, width, and breakout checks.
- Persist qualifying range records and optionally failure metadata later.

### 5. Scoring Flow

- Score only qualified ranges for MVP.
- Compute weighted components and derived sub-scores.
- Persist score outputs in `range_scores`.

### 6. Setup Flow

- Evaluate long and short conditions using the latest completed candle in the qualified range.
- Compute entries, stops, and targets.
- Persist setup rows in `trade_setups`.

### 7. UI Flow

- Query the latest stored scan results.
- Render screener rows, stock details, score explanations, and charts.
- Optionally augment the display with a live quote positioning overlay without recomputing analytics.

## Scan Flow

The MVP scan can run as a simple local command or scheduled script.

Recommended order:

1. refresh stock universe if needed
2. ingest completed historical bars
3. compute indicators
4. detect ranges
5. score qualified ranges
6. generate setups
7. persist scan metadata and timestamps

The scan should be idempotent for the same bar set and configuration.

## Storage Flow

- SQLite is the default local store.
- Write operations should be done in clear service boundaries rather than directly from Streamlit pages.
- Query helpers should support:
  - latest ranked ranges
  - latest scan timestamp
  - detail view by ticker and timeframe
  - chart history for a ticker
  - latest setup and optional alert records

## Deployment Notes

### MVP Local Deployment

- one Python environment
- one SQLite database file
- one Streamlit process
- optional local scheduled script or cron job for scans

### Future Deployment

- SQLite can be replaced with PostgreSQL with minimal model changes if queries and models remain portable.
- A future FastAPI layer can expose scan results for other clients, but that is outside the MVP core path.

## Suggested Folder Structure

```text
range-trading-app/
  README.md
  .gitignore
  .env.example
  requirements.txt
  pyproject.toml
  docs/
    PRD.md
    ARCHITECTURE.md
    DATA_ARCHITECTURE.md
    APP_SPEC.md
    DB_SCHEMA.md
    TASKS.md
    DECISIONS.md
  app/
    __init__.py
    main.py
    pages/
    components/
    services/
    models/
    utils/
    config/
  data/
    seeds/
    sample/
  scripts/
  tests/
```

## Design Principles

- Streamlit-first, not API-first
- persisted analytics, not heavy recomputation in-page
- explicit provider separation between historical bars and live quotes
- deterministic calculations based on completed candles
- simple local workflow over premature infrastructure
