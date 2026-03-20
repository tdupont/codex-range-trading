# Architecture Decision Records

## ADR-001: Streamlit-First MVP Architecture

- Status: Accepted
- Date: 2026-03-19

Decision:

- Build the MVP as a Streamlit-first Python application in a single repository.

Rationale:

- The product is primarily a local analytics and visualization tool.
- Streamlit reduces surface area compared with maintaining separate frontend and backend apps.
- A single-process local workflow is easier for one developer to build and debug.

Implications:

- Business logic must still live outside page files.
- A future FastAPI layer remains possible but is not required for MVP.

## ADR-002: S&P 500-Only Universe

- Status: Accepted
- Date: 2026-03-19

Decision:

- Limit MVP scans to S&P 500 constituents.

Rationale:

- Keeps data volume and UX manageable.
- Matches the product goal of a clear, focused first release.

Implications:

- Universe refresh logic should remain extensible, but no extra universes should be added in MVP work by default.

## ADR-003: Daily-First Scanning

- Status: Accepted
- Date: 2026-03-19

Decision:

- Daily candles are required and are the default scan mode.
- Weekly and monthly are optional supported modes if they can reuse the same pipeline cleanly.

Rationale:

- The product idea centers on end-of-day range trading.
- Daily data is simpler to source, test, and explain.

Implications:

- Config, storage, and query layers should include a `timeframe` field from the start.

## ADR-004: Rule-Based Detection Before Anything Smarter

- Status: Accepted
- Date: 2026-03-19

Decision:

- Use a deterministic rule-based range detection engine for MVP.

Rationale:

- Rules are transparent, testable, and aligned with the user’s requested detection logic.
- Machine learning is explicitly out of scope.

Implications:

- Thresholds must be configurable and documented.
- Output should be explainable per component and condition.

## ADR-005: Support/Resistance Zones Instead Of Lines

- Status: Accepted
- Date: 2026-03-19

Decision:

- Represent support and resistance as ATR-based zones rather than single price lines.

Rationale:

- Range interaction is naturally fuzzy.
- Zone-based logic is more realistic for touches, entries, and stops.

Implications:

- Charts, persistence, and setup logic must all handle high/low zone bounds.

## ADR-006: Composite Score With Sub-Scores

- Status: Accepted
- Date: 2026-03-19

Decision:

- Use a 0-100 weighted composite range score plus `Range Validity Score`, `Tradeability Score`, and `Opportunity Score`.

Rationale:

- A single rank is useful for scanning, but sub-scores keep the system explainable.

Implications:

- Persistence and UI should store and display component-level metrics.

## ADR-007: Historical Candles For Analytics, Live Quotes Only For Display

- Status: Accepted
- Date: 2026-03-19

Decision:

- All indicators, range detection, scoring, and setup generation must be based on completed historical candles only.
- If live quotes are used, they may only show current price relative to precomputed zones and setups.

Rationale:

- This avoids contaminating analytics with incomplete bars.
- It keeps the signal definition stable and reproducible.

Implications:

- Historical and live data providers must be explicitly separated in code and docs.
- UI labeling must distinguish scan-derived values from optional live quote context.

## ADR-008: SQLite For MVP

- Status: Accepted
- Date: 2026-03-19

Decision:

- Use SQLite as the default persistence layer for MVP.

Rationale:

- It minimizes setup friction for a local single-developer workflow.
- It is sufficient for an S&P 500 end-of-day screener.

Implications:

- Query design should remain portable to PostgreSQL.
- Avoid introducing SQLite-specific behavior into core business logic.
