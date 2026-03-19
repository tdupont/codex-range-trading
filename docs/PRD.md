# Product Requirements Document

## Product overview

Range Trading Screener is a web application that scans the S&P 500 daily, identifies stocks trading inside a stable range, scores them, and presents actionable long and short setups based on support and resistance zones.

The MVP is decision-support software, not an execution engine. It helps a user find candidates, understand why they were selected, and inspect the range structure behind each setup.

## Goals

- Reduce the manual effort required to find range-bound S&P 500 stocks.
- Apply a consistent, transparent rule set for range detection and setup generation.
- Rank candidates so users can focus on the highest-quality range setups first.
- Expose the results through a clean API and a web dashboard.
- Keep the first version simple enough to implement and validate quickly.

## Non-goals

- Broker connectivity or order placement
- Automated trading or alert-driven execution
- Machine learning or predictive modeling
- Options analytics
- Intraday or multi-timeframe signal generation
- Portfolio tracking, PnL, or risk aggregation
- Coverage beyond the S&P 500 for MVP

## Target users

- Discretionary swing traders looking for daily range setups
- Independent traders who want a ranked watchlist instead of manual chart review
- Developers or analysts validating a rules-based screening workflow

## MVP scope

### In scope

- S&P 500 stock universe only
- Daily candles only
- OHLCV ingestion and storage
- Technical indicator computation
- Rule-based range detection
- Range score computation and ranking
- Support and resistance zone generation
- Simple long and short setup generation
- REST API for dashboard consumption
- Web dashboard for list and detail views

### Out of scope

- All items listed in Non-goals

## Feature requirements

### Market data ingestion

- The system must ingest daily OHLCV data for all tracked S&P 500 tickers.
- The system must preserve adjusted historical data assumptions in a consistent way. If the provider supplies adjusted and unadjusted values, ingestion must document which is used.
- The system must support re-running ingestion without duplicating rows.

### Technical analysis pipeline

- The system must compute at least ADX(14), SMA(20), ATR(14), and RSI(14).
- Indicator calculations must be reproducible and tied to a specific trade date and ticker.
- Derived metrics used by the range engine must be stored or reproducible from stored inputs.

### Range detection

A stock is considered range-bound only when all conditions are true:

- `ADX(14) < 20`
- `abs(slope(SMA(20))) < configured_threshold`
- Over the last 30 trading days, at least 90% of closes remain inside the rolling 30-day high/low bounds
- At least 2 touches near support
- At least 2 touches near resistance
- Range width is at least `1.5 * ATR(14)`

Definitions for MVP:

- `upper_bound = highest high over lookback`
- `lower_bound = lowest low over lookback`
- `support_zone = [lower_bound, lower_bound + 0.3 * ATR]`
- `resistance_zone = [upper_bound - 0.3 * ATR, upper_bound]`
- `midline = (upper_bound + lower_bound) / 2`

Touch rules for MVP:

- A support touch occurs when the candle low or close enters the support zone.
- A resistance touch occurs when the candle high or close enters the resistance zone.
- Multiple consecutive days in the same zone should not all count as separate touches unless separated by a configurable cooldown or a move back toward the midline.

### Scoring and ranking

The system must compute a composite range score from 0 to 100 using these weighted components:

- Touch quality: 30%
- Trend weakness / ADX: 20%
- Containment quality: 15%
- Range width vs ATR: 15%
- Liquidity: 10%
- Current opportunity location: 10%

The system must also expose:

- Range Validity Score
- Tradeability Score
- Opportunity Score

Scoring must be explainable. The dashboard and API must be able to show component values, not just a final number.

### Setup generation

Long setup criteria:

- Current price is inside the support zone
- `RSI < 40`
- Basic bullish rejection condition

Short setup criteria:

- Current price is inside the resistance zone
- `RSI > 60`
- Basic bearish rejection condition

MVP rejection assumptions:

- Bullish rejection: close > open and lower wick is larger than the candle body
- Bearish rejection: close < open and upper wick is larger than the candle body

Targets:

- `target_1 = midline`
- `target_2 = opposite side of range`

Stops:

- Long stop = support zone bottom - `0.5 * ATR`
- Short stop = resistance zone top + `0.5 * ATR`

### Dashboard

The UI must provide:

- A ranked range list view
- Filters for score, liquidity, and setup direction availability
- A detail view for a selected ticker
- Candlestick chart with support zone, resistance zone, midline, and setup levels
- Clear explanation of why the ticker qualified

### API

The API must provide endpoints for health, ranges, range details, opportunities, and alerts.

## Functional requirements

- The system must maintain a canonical stock list for the S&P 500 universe.
- The system must support daily scheduled scans and manual re-scan triggers in development.
- The range engine must produce deterministic output for the same input dataset and config.
- The API must allow filtering and pagination for ranked results.
- The UI must read from the API only; detection logic must not be duplicated in the frontend.
- Alerts may be simple persisted events for when a ticker newly enters a long or short opportunity state.

## Non-functional requirements

- Prefer simple, observable modules over highly abstracted architecture.
- Target a full daily scan runtime that is practical for a single-service MVP deployment.
- Persist enough metadata to debug why a ticker passed or failed the screen.
- Use PostgreSQL as the system of record.
- Maintain clear separation between ingestion, indicators, detection, scoring, setup generation, and presentation.
- Make configuration explicit through environment variables and documented defaults.

## Acceptance criteria

- A developer can ingest and store daily OHLCV data for the S&P 500.
- A developer can run the indicator pipeline and persist derived values.
- The range detector identifies qualifying tickers using the documented rules.
- Each qualifying ticker has support/resistance zones, range metadata, and score components.
- The API returns ranked ranges and single-ticker range details in documented shapes.
- The frontend can render a ranked list and a ticker detail chart using API data only.
- Long and short opportunities include entry zone, stop, and two targets.
- Documentation is sufficient for a new coding agent to implement the system without guessing core product logic.

## Definition of done

The MVP is done when all of the following are true:

- The backend service runs locally with PostgreSQL.
- A scheduled or manually triggered scan can refresh the latest S&P 500 daily range results.
- The API returns health, range list, range detail, opportunities, and alerts endpoints in stable documented shapes.
- The frontend displays the latest ranked candidates and detail charts for a selected ticker.
- Core logic is covered by automated tests for indicator input handling, range detection, scoring, and API serialization.
- Documentation remains aligned with implementation.

## Assumptions

- End-of-day data freshness is acceptable for MVP.
- S&P 500 membership can be refreshed periodically rather than intraday.
- Daily range analysis is based on trading days present in the provider dataset, not calendar days.
- Liquidity can be approximated with average daily dollar volume in the MVP.

## Data Provider Abstraction

Provider selection is intentionally deferred. The implementation should define a provider interface that can:

- list or refresh the S&P 500 universe
- fetch historical daily OHLCV candles for one or many tickers
- report provider-specific metadata such as timezone, adjustment behavior, and last available trade date

Business logic must consume normalized daily bars and must not depend on a provider SDK directly. Any provider-specific mapping, throttling, and retry behavior belongs in the adapter layer.

## Future work

Clearly outside the MVP:

- Expanded universes such as ETFs, Russell 1000, or custom watchlists
- Multi-timeframe confirmation
- Notifications via email, Slack, or push
- User accounts and saved views
- Execution workflows
