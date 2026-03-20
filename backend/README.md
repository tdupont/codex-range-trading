# Backend

This directory will hold the FastAPI service, database models, domain logic, and tests for the Range Trading Screener MVP.

## Purpose

- ingest and normalize daily S&P 500 market data
- compute technical indicators
- detect range-bound stocks
- score and rank qualified ranges
- generate trade setups and alert events
- expose the latest state through a REST API

## Suggested implementation order

1. `app/core/` for settings and shared constants
2. `app/db/` and Alembic wiring
3. `app/models/` and migrations
4. `app/services/` for ingestion, indicators, detection, scoring, and setups
5. `app/api/` schemas and routes
6. `app/jobs/` orchestration for scheduled scans

## Module boundaries

- Route handlers should stay thin.
- Business logic belongs in services.
- ORM models define storage, not business rules.
- Indicator and scoring formulas should remain isolated and unit-tested.

## Local backend workflow

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
alembic upgrade head
python -m app.jobs.run_scan
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Implemented MVP modules

- `app/core/`: settings and shared constants
- `app/db/`: SQLAlchemy base and session management
- `app/models/`: ORM models for all documented MVP tables
- `app/services/`: provider abstraction, Stooq historical provider, local seed fallback provider, ingestion, indicators, range detection, scoring, setups, alerts, and scan orchestration
- `app/api/`: health, ranges, range detail, opportunities, and alerts routes
- `app/jobs/run_scan.py`: local seed/init scan entrypoint

## Market data source of truth

- `MARKET_DATA_PROVIDER=stooq` is the default runtime source for real daily OHLCV prices.
- `MARKET_DATA_PROVIDER=local_seed` remains available only for deterministic offline/demo runs.
- The UI displays persisted scan snapshots, so scan jobs must run against a real provider if you expect realistic closes in the API and frontend.
