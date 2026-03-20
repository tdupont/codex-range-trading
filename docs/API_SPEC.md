# API Specification

## Status

This document is intentionally non-authoritative for the MVP.

The repository is currently planned as a Streamlit-first application without a mandatory backend API. If a future FastAPI service is introduced, its contract should be documented here at that time.

## Current Guidance

- Do not treat an API layer as required for MVP delivery.
- Implement the MVP directly against the Streamlit-first architecture described in `docs/ARCHITECTURE.md`.
- If an API is later added for integration or deployment reasons, it should read persisted scan results rather than re-running analytics inside request handlers.

## Possible Future Endpoints

Future work only:

- health
- latest ranges
- range detail by ticker
- setups
- alerts

Any future API must preserve the same data separation rules in `docs/DATA_ARCHITECTURE.md`, especially the distinction between historical analytics inputs and optional live quote display data.
