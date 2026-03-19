# Architecture Decision Records

## ADR-001: Daily timeframe first

- Date: 2026-03-10
- Status: Accepted

Context:

The product goal is to identify clean, explainable range setups quickly. Supporting intraday data would materially increase ingestion volume, scheduling complexity, and noise in the first version.

Decision:

The MVP will use daily candles only.

Consequences:

- Indicator and range logic can be implemented with simpler data pipelines.
- End-of-day refresh is sufficient for the first release.
- Intraday alerts and execution-style workflows are explicitly deferred.

## ADR-002: S&P 500 only

- Date: 2026-03-10
- Status: Accepted

Context:

A constrained universe reduces implementation complexity and helps keep liquidity reasonably high for early validation.

Decision:

The MVP will screen S&P 500 constituents only.

Consequences:

- Universe management remains simple.
- Liquidity filters can be less defensive than in a broader market scan.
- Support for ETFs, custom lists, and broader equities is future work.

## ADR-003: Rule-based detection first

- Date: 2026-03-10
- Status: Accepted

Context:

The first version needs transparent logic that can be debugged, tested, and explained to users without model training or opaque heuristics.

Decision:

Range detection will be fully rule-based using ADX, SMA slope, containment, touch counts, and width versus ATR.

Consequences:

- Output is explainable and deterministic.
- Threshold tuning can be done through configuration.
- Machine learning is out of scope until the baseline workflow is validated.

## ADR-004: Support and resistance as zones, not lines

- Date: 2026-03-10
- Status: Accepted

Context:

Real price behavior is not precise to a single level. Using lines would create brittle touch logic and unrealistic setup triggers.

Decision:

Support and resistance will be modeled as ATR-based zones:

- support zone = `[lower_bound, lower_bound + 0.3 * ATR]`
- resistance zone = `[upper_bound - 0.3 * ATR, upper_bound]`

Consequences:

- Touch counting is more realistic.
- Setup entry logic aligns with practical trading behavior.
- Chart overlays should render shaded bands rather than thin lines.

## ADR-005: Composite score design

- Date: 2026-03-10
- Status: Accepted

Context:

Users need a single ranking number, but also need to understand whether quality comes from structure, liquidity, or current location within the range.

Decision:

The MVP will use a 0 to 100 composite range score with weighted components:

- touch quality: 30%
- trend weakness / ADX: 20%
- containment quality: 15%
- range width vs ATR: 15%
- liquidity: 10%
- current opportunity location: 10%

The system will also expose Range Validity Score, Tradeability Score, and Opportunity Score.

Consequences:

- Ranking is concise while remaining inspectable.
- Score component storage is required in the database and API.
- Weight tuning can evolve later under explicit versioning.

## ADR-006: FastAPI + Next.js stack

- Date: 2026-03-10
- Status: Accepted

Context:

The project needs a Python-centric analytics backend and a modern web frontend that can render tabular and chart-heavy views without unnecessary complexity.

Decision:

The MVP stack will be:

- Backend: Python, FastAPI, pandas, numpy, SQLAlchemy, Alembic, PostgreSQL
- Frontend: Next.js, TypeScript, Tailwind CSS, candlestick chart library

Consequences:

- Analytics logic stays close to the Python data ecosystem.
- The frontend remains decoupled and consumes the backend via REST.
- Local development should treat backend and frontend as separate apps inside one monorepo.
