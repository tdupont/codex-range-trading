# Implementation Tasks

This file breaks the MVP into sequential phases. Complete phases in order unless there is a clear reason to parallelize.

## Phase 1: Project Setup

- [x] Create Streamlit-first repository structure
- [x] Create core planning docs
- [x] Add root Python packaging files
- [x] Add `.env.example`
- [ ] Add linting and test config
- [ ] Add sample seed files for S&P 500 universe
- [ ] Add basic settings loader

## Phase 2: Data Layer

- [ ] Define domain models for stocks, bars, indicators, ranges, scores, and setups
- [ ] Define persistence models or SQLAlchemy tables
- [ ] Create SQLite connection/session utilities
- [ ] Create repository/query helpers for latest screener and detail views
- [ ] Add migration/bootstrap strategy for SQLite schema creation

## Phase 3: Ingestion

- [ ] Implement S&P 500 universe loading
- [ ] Implement `HistoricalMarketDataProvider` abstraction
- [ ] Create a local/mock provider for development
- [ ] Add historical OHLCV normalization and upsert logic
- [ ] Add ingestion scripts and basic logging

## Phase 4: Indicators

- [ ] Compute SMA(20)
- [ ] Compute ATR(14)
- [ ] Compute ADX(14)
- [ ] Compute RSI(14)
- [ ] Compute normalized SMA slope
- [ ] Compute net drift over the 30-bar window
- [ ] Compute liquidity helper metrics
- [ ] Persist indicator snapshots

## Phase 5: Range Detection

- [ ] Implement 30-bar upper/lower bound calculation
- [ ] Implement support and resistance zone generation
- [ ] Implement touch counting with separation rules
- [ ] Implement containment and recent breakout checks
- [ ] Implement range width vs ATR validation
- [ ] Implement drift vs range-width validation
- [ ] Persist qualified range results
- [ ] Decide whether to store rejected symbols with reasons

## Phase 6: Scoring

- [ ] Implement touch quality component
- [ ] Implement trend weakness / ADX component
- [ ] Implement containment quality component
- [ ] Implement range width vs ATR component
- [ ] Implement liquidity component
- [ ] Implement current opportunity location component
- [ ] Implement composite `range_score`
- [ ] Implement `Range Validity Score`
- [ ] Implement `Tradeability Score`
- [ ] Implement `Opportunity Score`

## Phase 7: Persistence And Query Layer

- [ ] Add write paths for ranges, scores, and setups
- [ ] Add latest-scan query methods for screener view
- [ ] Add symbol detail query methods
- [ ] Add scan metadata persistence
- [ ] Add optional alerts placeholder persistence

## Phase 8: Streamlit UI

- [ ] Build app shell and navigation
- [ ] Build screener page
- [ ] Add sidebar filters
- [ ] Add score and setup summary components
- [ ] Build stock detail page
- [ ] Show scan metadata and data freshness info

## Phase 9: Charts

- [ ] Create Plotly candlestick chart component
- [ ] Overlay support and resistance zones
- [ ] Overlay midline
- [ ] Overlay entry, stop, and target levels
- [ ] Optionally overlay live quote positioning as display-only context

## Phase 10: Polish And Testing

- [ ] Add unit tests for indicators
- [ ] Add unit tests for range detection
- [ ] Add unit tests for scoring
- [ ] Add integration tests for persistence/query flows
- [ ] Add smoke tests for Streamlit app boot
- [ ] Review docs for implementation drift
- [ ] Tighten defaults and configs based on observed outputs
