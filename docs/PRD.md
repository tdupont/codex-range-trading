# Product Requirements Document

## Product Overview

Range Trading Screener is a Streamlit app that scans the S&P 500 for stocks trading inside defined price ranges, ranks those candidates, and presents simple long and short setups based on support and resistance zones.

The MVP is a decision-support tool. It is not a trading system, broker integration, or alert execution platform. The core job of the product is to turn daily historical market data into a ranked, reviewable list of range-bound stocks with transparent setup logic.

## Goals

- Reduce manual chart review needed to find range-bound S&P 500 stocks.
- Use a transparent, rule-based process that another developer can implement and verify.
- Produce ranked candidates rather than a flat pass/fail list.
- Show support and resistance zones, not just labels or single price levels.
- Keep the MVP simple enough for one developer to build and run locally.

## Non-Goals

- Broker integration
- Auto execution
- Machine learning or predictive models
- Options analysis
- Intraday signal generation
- Portfolio tracking
- User authentication
- Multi-user collaboration
- Universe expansion beyond the S&P 500 in MVP

## Target Users

- Independent traders reviewing end-of-day opportunities
- Swing traders looking for bounded daily range setups
- Developers validating a rules-based market screening workflow

## MVP Scope

### In Scope

- S&P 500 universe only
- Daily candles as the primary supported mode
- Weekly and monthly selectable modes if implemented without compromising the daily-first architecture
- Historical OHLCV ingestion
- Technical indicator computation
- Range detection
- Range scoring and ranking
- Support and resistance zone generation
- Simple long and short setup generation
- Local persistence of scan outputs
- Streamlit dashboard
- Plotly chart visualizations
- Optional latest quote positioning relative to precomputed zones

### Out Of Scope

- Any feature listed in Non-Goals
- Mandatory separate backend API service for MVP
- Real-time streaming analytics

## Feature Requirements

### Market Universe

- The app must operate on the S&P 500 only for MVP.
- The universe source must be refreshable and stored locally.
- The system should allow inactive tickers to remain in storage for auditability rather than deleting history.

### Historical Data Ingestion

- The app must ingest OHLCV bars for the chosen timeframe.
- Daily bars are required.
- Weekly and monthly can be added as alternate scan modes if they use the same provider abstraction and persistence model.
- Ingestion must be repeatable without duplicating bars.
- Historical bars must be stored with provider metadata and ingestion timestamps.

### Indicators

- The app must compute at least ADX(14), SMA(20), ATR(14), and RSI(14).
- Derived fields used for detection or scoring must be reproducible from stored inputs.
- Indicator snapshots must be tied to ticker, timeframe, and bar date.

### Range Detection

A stock qualifies as range-bound only when all of the following are true for the scan timeframe:

- `ADX(14) < 20`
- normalized slope of `SMA(20)` is near zero
- support and resistance are derived from a fixed 30-bar lookback window
- there are at least 2 or 3 separated touches at both boundaries
- touch tolerance is ATR-based
- range width is at least `2 x ATR(14)`
- net 30-bar drift is small relative to range width
- there is no recent breakout close outside the zone

Definitions for MVP:

- `upper_bound = highest high over lookback`
- `lower_bound = lowest low over lookback`
- `support_zone = [lower_bound, lower_bound + 0.3 * ATR]`
- `resistance_zone = [upper_bound - 0.3 * ATR, upper_bound]`
- `midline = (upper_bound + lower_bound) / 2`

Touch guidance:

- Touches must be separated to avoid counting clusters as multiple independent tests.
- A touch should be counted when price enters the relevant zone within ATR-based tolerance.
- The implementation should use a configurable bar-separation rule and record the chosen value in code and docs.

### Scoring

The app must produce a `range_score` from 0 to 100 using these weights:

- touch quality: 30%
- trend weakness / ADX: 20%
- containment quality: 15%
- range width vs ATR: 15%
- liquidity: 10%
- current opportunity location: 10%

The app must also expose:

- Range Validity Score
- Tradeability Score
- Opportunity Score

Scores must be explainable. The user should be able to inspect component-level values.

### Setup Generation

Long setup conditions:

- price is in the support zone
- RSI < 40
- a basic bullish rejection condition is true

Short setup conditions:

- price is in the resistance zone
- RSI > 60
- a basic bearish rejection condition is true

Targets:

- target 1 = midline
- target 2 = opposite side of range

Stops:

- long stop = support zone bottom - `0.5 * ATR`
- short stop = resistance zone top + `0.5 * ATR`

The initial bullish and bearish rejection rules should be kept simple, deterministic, and based on completed candles only.

### Dashboard

- The app must provide a screener view with ranked results.
- The app must provide a stock detail view with chart and score breakdown.
- The app must expose the latest completed scan time.
- The app may optionally show a latest quote and quote-to-zone distance if sourced separately from live quote data.

## Functional Requirements

- The system must maintain a canonical S&P 500 stock list.
- The system must support local scan runs initiated by scripts or manual commands.
- The analytics pipeline must be deterministic for the same input data and config.
- Results must be queryable locally without recomputing everything inside the UI request path.
- Streamlit page code must consume service-layer outputs rather than embedding full analytics logic in the page.
- The app must make clear whether displayed price context is historical scan output or live quote positioning.

## Non-Functional Requirements

- Favor clarity over abstraction-heavy design.
- Optimize for a single-developer local workflow.
- Persist enough metadata to debug why a ticker qualified.
- Use SQLite by default for MVP.
- Keep room for future PostgreSQL migration without redesigning core entities.
- Keep data provider integration behind abstractions.
- Ensure charts and pages remain responsive for an S&P 500-sized result set.

## Acceptance Criteria

- A developer can set up the repo locally and run a Streamlit shell app.
- Historical OHLCV data can be ingested and stored locally for S&P 500 symbols.
- The indicator pipeline computes the documented indicators from completed candles.
- The range detector applies the documented qualification rules.
- Qualified ranges receive score components and a total score.
- Generated setups include entries, stop, and two targets.
- Results can be viewed in a Streamlit screener and a stock detail page.
- Documentation is concrete enough for another coding agent to implement the MVP without redefining the product.

## Definition Of Done

The MVP is done when all of the following are true:

- daily scans for the S&P 500 run locally end-to-end
- qualified ranges, scores, and setups are persisted in SQLite
- the Streamlit app shows a ranked screener and a detailed single-stock view
- charts display candles, support/resistance zones, midline, and setup levels
- tests cover core detection, scoring, and persistence behavior
- docs remain aligned with implementation choices

## Assumptions

- End-of-day workflows are acceptable for MVP.
- The daily timeframe is the primary operating mode.
- Weekly and monthly scans, if added, reuse the same calculations at different bar granularities.
- Liquidity can be approximated using average daily dollar volume or average share volume with documented assumptions.
- Provider selection is not fixed yet and will be handled through abstractions.

## Open Implementation Questions

- Which historical data provider will be the first real integration?
- What exact normalized SMA slope threshold produces acceptable false positive rates?
- Should MVP store only qualified ranges or all evaluated symbols with failure reasons?

These should be resolved in implementation phases and recorded in `docs/DECISIONS.md`.
