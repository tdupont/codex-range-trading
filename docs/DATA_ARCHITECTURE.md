# Data Architecture

## Purpose

This document defines how market data is separated, ingested, stored, and allowed to flow through the MVP. The most important rule is that analytics must use completed historical candles only.

## Core Data Separation

The system must explicitly separate two provider roles:

1. `HistoricalMarketDataProvider`
2. `LiveQuoteProvider`

They serve different purposes and must not be mixed.

## Historical OHLCV Data

Historical OHLCV data is used for:

- indicator calculations
- range detection
- support and resistance zone generation
- scoring
- setup generation
- chart history

Historical bars must be completed candles for the selected timeframe.

Examples:

- daily scan uses completed daily bars
- weekly scan uses completed weekly bars
- monthly scan uses completed monthly bars

## Live Quote Data

Live quote data is optional and display-only for MVP.

Live quotes may be used for:

- showing the current price relative to support and resistance zones
- showing distance from current price to entry, stop, or target
- showing whether price is near support or resistance right now

Live quotes must not be used for:

- indicator calculations
- range detection
- boundary calculations
- score recalculation
- setup recalculation
- touch counting

## Data Provider Abstraction

If the specific vendor is not chosen yet, implement interfaces first.

### `HistoricalMarketDataProvider`

Required responsibilities:

- return completed OHLCV bars for a ticker and timeframe
- return bulk OHLCV bars for a list of tickers if supported
- expose provider metadata such as timezone and adjustment handling
- report the most recent completed bar date available

Suggested interface:

```python
class HistoricalMarketDataProvider(Protocol):
    def fetch_bars(
        self,
        ticker: str,
        timeframe: str,
        start_date: date,
        end_date: date,
    ) -> list[HistoricalBar]:
        ...

    def fetch_bars_bulk(
        self,
        tickers: list[str],
        timeframe: str,
        start_date: date,
        end_date: date,
    ) -> dict[str, list[HistoricalBar]]:
        ...

    def get_last_completed_bar_date(self, timeframe: str) -> date:
        ...
```

### `LiveQuoteProvider`

Required responsibilities:

- return the latest quote for a ticker
- return quote timestamp and provider metadata

Suggested interface:

```python
class LiveQuoteProvider(Protocol):
    def fetch_quote(self, ticker: str) -> LiveQuote:
        ...
```

### Normalized Models

`HistoricalBar` should contain:

- ticker
- timeframe
- bar date
- open
- high
- low
- close
- adjusted close if available
- volume
- provider
- provider timezone
- completed flag

`LiveQuote` should contain:

- ticker
- quote timestamp
- last price
- bid and ask if available
- provider

## Rules For Data Usage

### Allowed

- calculate ADX, SMA, ATR, RSI from stored completed historical bars
- detect ranges from the latest completed historical lookback window
- score ranges from historical bars and stored indicators
- generate setups from historical data only
- display current quote relative to an already-computed range

### Not Allowed

- using today’s partial bar in a daily scan before market close
- mixing a live quote into SMA, ATR, RSI, or ADX calculations
- shifting support or resistance because the latest quote crossed a zone
- recalculating range score from a non-persisted live quote

## Refresh Cadence Guidance

### Historical Data

- Daily mode: refresh after the market session is complete and the provider marks the bar complete
- Weekly mode: refresh only after the weekly bar is complete
- Monthly mode: refresh only after the monthly bar is complete

### Live Quotes

- refresh on page load or user action if enabled
- treat live quote freshness separately from scan freshness

## Storage Model

The app should persist at least the following layers:

- `ohlcv`: normalized completed bars
- `indicators`: computed indicator snapshots
- `ranges`: range geometry and qualification outputs
- `range_scores`: composite score and components
- `trade_setups`: derived long/short setups

Historical data and live quotes should not share the same table in MVP.

If live quotes are persisted later, use a separate quote cache table.

## Timezone Guidance

- Store provider timezone metadata where useful.
- Normalize bar dates to trading dates, not local machine timestamps.
- Store timestamps in UTC where timestamp precision matters.
- Be explicit when a bar date refers to market session date versus ingestion time.

## Completed-Candle Considerations

- A bar should only enter the analytics pipeline once it is complete for its timeframe.
- If a provider exposes incomplete bars, mark them as incomplete and exclude them from analytics queries.
- The scan job should use the provider’s last completed bar date rather than assuming calendar alignment.

## Scan Consistency Guidance

- A single scan run should use one consistent completed-bar cutoff per timeframe.
- Do not allow one ticker to use a newer completed bar than another within the same scan if that inconsistency can be avoided.
- Persist the bar date used for the range and setup calculation.

## Future Data Extensions

Clearly outside MVP but compatible with this model:

- cached live quote table
- provider failover
- corporate action audit tracking
- PostgreSQL-backed storage
