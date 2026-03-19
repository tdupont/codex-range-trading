# Range Trading Screener

Range Trading Screener is a web app for identifying S&P 500 stocks that are trading in well-defined daily ranges, ranking them, and surfacing simple long and short setups around support and resistance zones.

This repository is intentionally being started from documentation first. The immediate goal is to make the MVP implementable by any future coding agent without re-deciding the product scope or system shape.

## Source of truth

Before writing code, read these files in order:

1. `docs/PRD.md`
2. `docs/ARCHITECTURE.md`
3. `docs/TASKS.md`

Those three documents define the MVP scope, system boundaries, and implementation sequence. If a new idea conflicts with them, follow the docs unless the docs are explicitly updated.

## MVP guardrails

- Build the MVP only: S&P 500 universe, daily candles, rule-based range detection, API, and dashboard.
- Do not add broker integration, auto execution, ML, options, intraday logic, or portfolio tracking unless they are clearly marked as future work and explicitly approved.
- Unknown implementation details should be handled by making the smallest reasonable assumption and documenting it in `docs/DECISIONS.md`.

## Repository layout

- `docs/`: product, architecture, API, schema, task plan, and ADR-style decisions
- `backend/`: FastAPI service, domain logic, persistence layer, and tests
- `frontend/`: Next.js dashboard UI, data access layer, and chart components
- `docker-compose.yml`: local PostgreSQL bootstrap for development
- `.env.example`: shared environment variable template for the repo

## Working agreement for coding agents

- Treat `docs/PRD.md`, `docs/ARCHITECTURE.md`, and `docs/TASKS.md` as the implementation contract.
- Prefer incremental delivery by phase from `docs/TASKS.md`.
- Update documentation when implementation decisions materially change behavior, storage, or API shape.
- Keep modules focused. Detection, scoring, setup generation, API serialization, and UI rendering should remain separate concerns.
- If a data provider choice is needed, implement against the abstraction described in the docs rather than coupling business logic to one vendor.

## Current status

The repository currently contains the initial structure, planning docs, and a few lightweight stubs to anchor backend and frontend work. The next implementation step is Phase 1 in `docs/TASKS.md`: bootstrap the backend and frontend runtimes, wire local development dependencies, and make the first health check path runnable end to end.
