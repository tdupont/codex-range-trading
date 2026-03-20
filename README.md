# Range Trading Screener

Range Trading Screener is a Streamlit-first Python app for scanning the S&P 500, identifying stocks trading inside well-defined ranges, ranking them, and presenting simple long and short setups around support and resistance zones.

This repository is intentionally being reset around documentation-first MVP planning. The goal of this step is to give future coding agents a clean implementation path without re-deciding scope, architecture, or data rules.

## Source Of Truth

Future coding work should start from these files:

1. `docs/PRD.md`
2. `docs/ARCHITECTURE.md`
3. `docs/DATA_ARCHITECTURE.md`
4. `docs/TASKS.md`

If implementation ideas conflict with those documents, update the docs first or defer the enhancement.

## MVP Guardrails

- Stay inside MVP scope before adding enhancements.
- Universe is S&P 500 only.
- Daily timeframe is the primary mode. Weekly and monthly are optional extensions if they fit the same architecture cleanly.
- Analytics, indicators, range detection, scoring, support/resistance, and setup generation must use completed historical candles only.
- Live quotes, if used, are display-only inputs for showing current price relative to already computed zones and setups.
- Do not add broker integration, auto execution, machine learning, options, intraday signals, portfolio tracking, or auth in the MVP.

## Repository Layout

The repository is being organized around a single-developer local workflow:

- `docs/`: product, architecture, data, database, app, tasks, and decision records
- `app/`: Streamlit app code, analytics services, models, utilities, and config
- `data/`: local seeds and sample data files for development
- `scripts/`: CLI helpers such as ingestion, scans, or seed refresh jobs
- `tests/`: automated tests

There are older exploratory `backend/` and `frontend/` directories in the repo. They are not the source of truth for the MVP plan. New implementation work should target the Streamlit-first structure documented above unless the architecture docs are intentionally revised.

## Working Agreement For Coding Agents

- Read `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/DATA_ARCHITECTURE.md`, and `docs/TASKS.md` before making non-trivial changes.
- Implement by phase from `docs/TASKS.md`.
- Keep business logic out of Streamlit page files. UI, analytics, persistence, and provider adapters should remain separate concerns.
- Use the documented provider abstractions rather than coupling analytics directly to one vendor SDK.
- Record important architectural or product-level changes in `docs/DECISIONS.md`.

## Local Setup

1. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a local environment file:

```bash
cp .env.example .env
```

4. Run a local scan to populate SQLite:

```bash
python -m scripts.run_scan
```

5. Run the Streamlit app:

```bash
streamlit run app/main.py
```

Notes:

- The default MVP storage target is SQLite.
- If an older local `.env` still points at PostgreSQL from previous experiments, the MVP will fall back to `sqlite:///data/range_trading.db` when the PostgreSQL driver is unavailable.
- The bundled local provider uses a static S&P 500 seed file plus deterministic synthetic historical bars so the app remains runnable without market-data credentials.

## Near-Term Development Path

- Phase 1: finish base project setup and local config
- Phase 2-7: implement data providers, ingestion, indicators, detection, scoring, and SQLite persistence
- Phase 8-9: add the Streamlit screener, detail views, and Plotly charts
- Phase 10: harden tests, docs, and polish

## Completed Candle Rule

All MVP analytics must be derived from completed historical candles only. This rule applies to:

- indicators
- range detection
- support and resistance zones
- scoring
- setup generation

If a live quote provider is added, it may only show where the latest quote sits relative to precomputed zones, stops, and targets. It must not change the underlying analytics until the corresponding bar is complete and persisted as historical market data.
