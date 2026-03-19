# Implementation Tasks

## Phase 1: project setup

- [ ] Finalize backend dependency management choice and project bootstrap
- [ ] Finalize frontend dependency management choice and project bootstrap
- [ ] Create FastAPI app entrypoint and API router registration
- [ ] Create Next.js app shell and shared layout
- [ ] Add database connection settings and environment loading
- [ ] Add SQLAlchemy base setup and Alembic initialization
- [ ] Add local PostgreSQL startup workflow using `docker-compose.yml`
- [ ] Make `GET /health` runnable locally

## Phase 2: backend data model

- [ ] Implement ORM models for `stocks`
- [ ] Implement ORM models for `ohlcv`
- [ ] Implement ORM models for `indicators`
- [ ] Implement ORM models for `ranges`
- [ ] Implement ORM models for `range_scores`
- [ ] Implement ORM models for `trade_setups`
- [ ] Implement ORM models for `alerts`
- [ ] Create first Alembic migration

## Phase 3: ingestion

- [ ] Implement the Data Provider Abstraction interface
- [ ] Add first concrete provider adapter
- [ ] Build S&P 500 universe refresh flow
- [ ] Build OHLCV historical fetch and upsert flow
- [ ] Handle idempotent re-runs and missing-day updates
- [ ] Add ingestion logging and failure reporting
- [ ] Add tests for normalization and upsert behavior

## Phase 4: indicators

- [ ] Implement indicator service using `pandas`, `numpy`, and chosen TA library
- [ ] Compute ADX(14), SMA(20), SMA slope, ATR(14), RSI(14)
- [ ] Compute average dollar volume for liquidity scoring
- [ ] Persist indicators by ticker and trade date
- [ ] Add tests for indicator edge cases and warm-up periods

## Phase 5: range detection

- [ ] Implement 30-day bound calculation
- [ ] Implement containment ratio calculation
- [ ] Implement support and resistance zone construction
- [ ] Implement touch counting with a cooldown or de-duplication rule
- [ ] Implement range qualification checks using all documented conditions
- [ ] Persist qualifying range snapshots
- [ ] Add unit tests for borderline qualification scenarios

## Phase 6: scoring

- [ ] Implement weighted component scoring
- [ ] Define score normalization rules to keep outputs between 0 and 100
- [ ] Implement Range Validity Score
- [ ] Implement Tradeability Score
- [ ] Implement Opportunity Score
- [ ] Persist score breakdowns with versioning
- [ ] Add tests for score stability and explainability

## Phase 7: API

- [ ] Implement `GET /health`
- [ ] Implement `GET /ranges` with filtering, sorting, and pagination
- [ ] Implement `GET /ranges/{ticker}` with score breakdown and chart payload
- [ ] Implement `GET /opportunities`
- [ ] Implement `GET /alerts`
- [ ] Standardize error responses
- [ ] Add API tests for happy path and not-found cases

## Phase 8: frontend

- [ ] Build dashboard page for ranked ranges
- [ ] Build filter controls
- [ ] Build ticker detail page
- [ ] Create typed API client for backend responses
- [ ] Render score summaries and setup cards
- [ ] Add loading, empty, and error states

## Phase 9: charts

- [ ] Integrate a candlestick chart library suitable for daily OHLCV
- [ ] Plot recent candles on the detail page
- [ ] Overlay support zone and resistance zone
- [ ] Overlay midline, stop, and targets when a setup is active
- [ ] Add tooltip or legend support for key values

## Phase 10: polish/testing

- [ ] Add end-to-end sanity checks across ingestion to UI
- [ ] Add seed or fixture data for local development
- [ ] Review logging and observability basics
- [ ] Review query performance and indexes
- [ ] Tighten API response consistency
- [ ] Review docs for implementation drift
- [ ] Prepare MVP deployment checklist

## Recommended order of execution

1. Complete Phases 1 and 2 before writing production range logic.
2. Finish Phases 3 through 6 before building most of the frontend.
3. Deliver API endpoints before chart polish.
4. Leave non-essential deployment hardening until the core screening loop works.

## Exit criteria by milestone

- Milestone A: local app boots, database connects, health endpoint works
- Milestone B: ingestion and indicators persist real daily data
- Milestone C: range detection and scoring produce ranked candidates
- Milestone D: API exposes list/detail/setup data
- Milestone E: frontend renders usable dashboard and charts
