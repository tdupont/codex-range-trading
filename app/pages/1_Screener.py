"""Screener page."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.bootstrap import ensure_project_root_on_path

ensure_project_root_on_path(__file__)

import streamlit as st

from app.components.tables import render_dataframe
from app.config.settings import settings
from app.services.storage_service import StorageService


storage = StorageService(settings)
storage.initialize_database()

st.title("Screener")
st.caption("Ranked qualified ranges from the latest completed scan.")

with storage.session_scope() as session:
    timeframe = st.sidebar.selectbox("Timeframe", settings.supported_scan_timeframes, index=0)
    frame = storage.screener_dataframe(session, timeframe)

if frame.empty:
    st.info("No scan results yet. Run a scan from the main dashboard first.")
    st.stop()

min_score = st.sidebar.slider("Minimum Score", 0, 100, 60)
setup_direction = st.sidebar.selectbox("Setup Direction", ["all", "long", "short"])
liquidity_floor = st.sidebar.number_input("Minimum Avg Dollar Volume", min_value=0, value=0, step=1_000_000)
near_support = st.sidebar.checkbox("Near Support")
near_resistance = st.sidebar.checkbox("Near Resistance")
max_rows = st.sidebar.slider("Max Rows", 10, 100, min(50, len(frame)))

filtered = frame.copy()
filtered = filtered[filtered["range_score"] >= min_score]
filtered = filtered[filtered["avg_dollar_volume_20"] >= liquidity_floor]
if setup_direction != "all":
    filtered = filtered[filtered["setup_direction"] == setup_direction]
if near_support:
    filtered = filtered[filtered["distance_to_support"] <= filtered["distance_to_resistance"]]
if near_resistance:
    filtered = filtered[filtered["distance_to_resistance"] <= filtered["distance_to_support"]]
filtered = filtered.head(max_rows)

st.write(f"{len(filtered)} rows shown from the latest `{timeframe}` scan.")
render_dataframe(
    filtered[
        [
            "ticker",
            "name",
            "latest_close",
            "range_score",
            "range_validity_score",
            "tradeability_score",
            "opportunity_score",
            "support_zone",
            "resistance_zone",
            "distance_to_support",
            "distance_to_resistance",
            "adx_14",
            "atr_14",
            "rsi_14",
            "avg_dollar_volume_20",
            "setup_direction",
            "setup_status",
        ]
    ]
)
