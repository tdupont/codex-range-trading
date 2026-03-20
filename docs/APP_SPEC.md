# App Specification

## App Structure

The MVP app is a Streamlit dashboard with a small number of focused views.

Recommended views:

- Screener
- Stock Detail
- Scan Status

Future work can add watchlist or alerts views without changing the MVP core flow.

## View Requirements

### Screener View

Purpose:

- show the latest ranked range candidates
- help users sort and filter opportunities quickly

Required content:

- latest scan timestamp
- timeframe selector
- ranked table of qualified stocks
- total result count
- quick summary metrics such as average score or number of long/short candidates

### Stock Detail View

Purpose:

- inspect one ticker in depth

Required content:

- ticker and company name
- latest range score and sub-scores
- support zone, resistance zone, and midline
- setup summary
- latest completed bar date
- optional live quote positioning section
- chart with overlays

### Scan Status View

Purpose:

- show operational state for local usage

Suggested content:

- latest completed scan time
- latest completed bar date used
- scan universe size
- count of qualified ranges
- last ingestion status

## Sidebar Filters

The sidebar should contain simple, high-value filters only.

Required filters:

- timeframe
- minimum range score
- setup direction: all, long, short
- minimum liquidity threshold
- sector filter if sector data is available
- only show active opportunities toggle

Optional filters:

- minimum touch count
- ADX ceiling
- near-support or near-resistance toggle

## Screener Table Requirements

Each row should support fast decision-making.

Recommended columns:

- rank
- ticker
- company name
- timeframe
- range score
- Range Validity Score
- Tradeability Score
- Opportunity Score
- support zone
- resistance zone
- latest completed close
- setup direction
- target summary
- liquidity metric
- latest scan date

Table behavior:

- sortable by score and key metrics
- filterable from sidebar inputs
- clicking a ticker opens the detail view

## Stock Detail Requirements

The detail view should make the qualification transparent.

Required sections:

- overview header
- score breakdown
- range geometry summary
- setup card
- candlestick chart
- recent bars table or compact statistics block

The qualification summary should explicitly show:

- ADX value
- SMA slope condition
- support touches
- resistance touches
- range width vs ATR
- drift vs range width
- breakout status

## Chart Requirements

Use Plotly for Streamlit compatibility.

Required chart features:

- candlestick chart
- support zone overlay
- resistance zone overlay
- midline overlay
- entry range overlay
- stop line
- target 1 and target 2 lines

Optional display-only overlay:

- latest live quote marker

The chart must make it obvious that support and resistance are zones, not single lines.

## Score Display Requirements

Display:

- total `range_score`
- Range Validity Score
- Tradeability Score
- Opportunity Score
- component scores with weight labels

Score UI guidance:

- use compact metric cards or badges
- do not hide component scores behind multiple clicks
- show both numeric values and enough labeling to explain what they mean

## Future Watchlist / Alerts Placeholders

Future work ideas that can be left as placeholders now:

- watchlist persistence for selected tickers
- alert subscriptions for entering support/resistance zones
- new setup notifications after a scan

These should be clearly labeled as future work and should not drive MVP architecture decisions.
