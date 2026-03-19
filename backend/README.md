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

## Immediate next step

Bootstrap the Python project, wire FastAPI, SQLAlchemy, and Alembic, then make the health endpoint run against local settings.
