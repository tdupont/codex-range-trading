# Frontend

This directory will hold the Next.js dashboard for browsing ranked ranges, inspecting individual tickers, and reviewing active opportunities.

## MVP responsibilities

- fetch range, setup, and alert data from the backend API
- render a ranked dashboard list
- render a ticker detail view with chart overlays
- show score breakdowns and active trade setup information

## Suggested implementation order

1. App shell and layout
2. Typed API client in `src/lib/`
3. Dashboard table and filters
4. Ticker detail route and score cards
5. Candlestick chart integration
6. Alerts view or alerts panel

## Frontend rules

- Do not duplicate range detection or scoring logic in the UI.
- Treat the backend API as the source of truth.
- Keep chart-specific data transformation in frontend utilities, not page components.

## Local frontend workflow

```bash
npm install
npm run dev
```

The frontend consumes the backend API only and renders:

- dashboard summary cards
- ranked ranges table
- top opportunities section
- alerts panel
- stock detail page with candlestick chart overlays
