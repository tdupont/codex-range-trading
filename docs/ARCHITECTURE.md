# Architecture

## High-level system architecture

The MVP is a monorepo with one backend service, one frontend application, and one PostgreSQL database.

Primary flow:

1. Ingest daily OHLCV data for the S&P 500.
2. Compute indicators and derived range metrics.
3. Run the range detection and scoring pipeline.
4. Persist range snapshots, setup candidates, and alert events.
5. Serve the latest results through a REST API.
6. Render list and detail views in the dashboard.

Logical components:

- Data provider adapter
- Ingestion pipeline
- Indicator engine
- Range detection engine
- Scoring engine
- Setup generation engine
- REST API layer
- Dashboard UI
- PostgreSQL persistence

## Backend modules

Suggested backend responsibilities:

- `app/api/`
  - FastAPI route handlers
  - request parsing, response serialization, status codes
- `app/core/`
  - settings, logging, constants, shared utilities
- `app/db/`
  - SQLAlchemy session management, base metadata, migrations integration
- `app/models/`
  - ORM models for stocks, ohlcv, indicators, ranges, scores, setups, alerts
- `app/schemas/`
  - Pydantic request/response schemas
- `app/services/`
  - domain services for ingestion, indicators, detection, scoring, setups, alerts
- `app/jobs/`
  - scheduled scan orchestration and batch workflows

Recommended service split:

- `universe_service`
- `market_data_service`
- `indicator_service`
- `range_detection_service`
- `scoring_service`
- `setup_service`
- `alert_service`

## Frontend modules

Suggested frontend responsibilities:

- `src/app/`
  - Next.js routes, layouts, and page composition
- `src/components/`
  - reusable UI pieces such as tables, filter bars, charts, score cards
- `src/lib/`
  - API client, type definitions, formatting helpers

Recommended page-level split:

- Dashboard page for ranked ranges
- Ticker detail page for one symbol
- Lightweight alerts page or panel for newly triggered opportunities

Recommended component split:

- `RangeTable`
- `RangeFilters`
- `ScoreBreakdownCard`
- `SetupSummaryCard`
- `CandlestickRangeChart`

## Data flow

### 1. Universe refresh

- Load or refresh the S&P 500 ticker list.
- Upsert rows into `stocks`.
- Mark inactive tickers rather than deleting history.

### 2. Market data ingestion

- Fetch normalized daily OHLCV data from the provider adapter.
- Upsert candles into `ohlcv` keyed by stock and trade date.
- Track the source, adjustment mode, and ingestion timestamp.

### 3. Indicator computation

- Read recent OHLCV history for each active ticker.
- Compute ADX, SMA, ATR, RSI, and any helper metrics required by scoring.
- Persist daily indicator snapshots in `indicators`.

### 4. Range detection

- Use the last 30 trading days and the latest indicator values.
- Compute upper and lower bounds, zones, touch counts, containment ratio, and range width.
- Persist a range snapshot in `ranges` only if the ticker currently qualifies, or persist qualification metadata if retaining failures is chosen later.

### 5. Scoring

- Compute weighted component scores.
- Persist total and sub-score values in `range_scores`.

### 6. Setup generation

- Determine whether a long or short setup is currently active.
- Compute entry area, stop, and targets.
- Persist rows in `trade_setups`.

### 7. Alert generation

- Compare the latest setup state against the prior scan state.
- Persist an alert event only when a setup is newly triggered or meaningfully changed.

### 8. API serving

- API reads the latest persisted scan state.
- Frontend consumes normalized API responses only.

## Background job / scan flow

The scan flow should run as a single orchestrated job for MVP.

Recommended sequence:

1. Refresh universe if due
2. Ingest latest OHLCV bars
3. Compute indicators
4. Detect ranges
5. Score ranges
6. Generate setups
7. Emit alerts
8. Mark scan run status and timing

Implementation note:

- For MVP, the orchestration can start as a synchronous CLI or scheduled process inside the backend project.
- If needed later, background execution can move to a queue-based worker without changing the core domain services.

## Deployment notes

### Local development

- PostgreSQL via `docker-compose.yml`
- Backend runs as a FastAPI service
- Frontend runs as a Next.js app against the local API

### MVP deployment

- A single backend app instance is sufficient if scan execution is scheduled off-hours or serialized.
- PostgreSQL should be a managed service or a persistent container-backed volume.
- Frontend can be deployed separately as a static-plus-server-rendered Next.js app.

### Operational notes

- Persist logs for scan failures and provider errors.
- Capture scan start/end time and row counts for ingestion and qualification.
- Keep configuration-driven thresholds out of route handlers and UI code.

## Suggested folder structure

```text
range-trading-app/
  docs/
  backend/
    app/
      api/
      core/
      db/
      jobs/
      models/
      schemas/
      services/
    tests/
  frontend/
    src/
      app/
      components/
      lib/
    public/
```

## Separation of concerns

- Provider adapters normalize raw vendor payloads into internal candle objects.
- Ingestion persists raw market history and should not decide whether a stock is tradable.
- Indicator services compute reusable metrics and do not rank stocks.
- Range detection decides qualification and geometry of the range.
- Scoring ranks already-detected candidates and exposes component explanations.
- Setup generation turns qualified ranges into directional trade ideas.
- API routes serialize persisted state and should not run heavy analytics inline.
- Frontend renders results and allows exploration; it must not reproduce backend calculations.

## Data Provider Abstraction

The backend should introduce an adapter interface before picking a concrete vendor. The interface should provide:

- `get_universe()`
- `get_daily_bars(ticker, start_date, end_date)`
- `get_daily_bars_bulk(tickers, start_date, end_date)` if supported
- metadata methods for timezone, corporate action handling, and provider limits

The rest of the system should operate on a provider-agnostic daily candle model with fields for ticker, trade date, open, high, low, close, volume, and optional adjusted close.

## Architectural assumptions

- Daily scans are acceptable; no streaming architecture is required.
- Persisted snapshots are preferred over purely on-demand computation so the UI remains responsive and debuggable.
- The first implementation should optimize clarity and correctness before micro-optimizing performance.
