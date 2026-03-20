"""Scan status page."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.bootstrap import ensure_project_root_on_path

ensure_project_root_on_path(__file__)

import streamlit as st

from app.config.settings import settings
from app.services.storage_service import StorageService


storage = StorageService(settings)
storage.initialize_database()

st.title("Scan Status")
st.caption("Operational visibility for recent local scan runs.")

with storage.session_scope() as session:
    runs = storage.scan_runs_dataframe(session)

if runs.empty:
    st.info("No scan runs recorded yet.")
else:
    st.dataframe(runs, use_container_width=True, hide_index=True)

st.subheader("Alerts / Watchlist")
st.write("Placeholder for future watchlist and alert workflows. Not implemented in the MVP.")
