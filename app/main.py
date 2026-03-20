"""Streamlit dashboard entry point."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.bootstrap import ensure_project_root_on_path

ensure_project_root_on_path(__file__)

import streamlit as st

from app.components.tables import render_dataframe
from app.config.logging import configure_logging
from app.config.settings import settings
from app.services.scan_service import ScanAlreadyRunningError, ScanService
from app.services.storage_service import StorageService


configure_logging(settings.log_level)
storage = StorageService(settings)
scan_service = ScanService(settings, storage)


def main() -> None:
    st.set_page_config(page_title="Range Trading Screener", layout="wide")
    storage.initialize_database()

    st.title("Range Trading Screener")
    st.caption("Streamlit-first S&P 500 range screener using completed historical candles only.")

    controls_col, info_col = st.columns([1, 2])
    with controls_col:
        timeframe = st.selectbox("Timeframe", settings.supported_scan_timeframes, index=0)
        if st.button("Run Scan", type="primary", use_container_width=True):
            try:
                with st.spinner("Running scan..."):
                    summary = scan_service.run_scan(timeframe)
            except ScanAlreadyRunningError as exc:
                st.warning(str(exc))
            else:
                st.success(
                    f"Scan complete for {summary.scan_bar_date}. "
                    f"{summary.ranges_detected} qualified ranges found."
                )
    with info_col:
        st.write(
            "The MVP persists locally to SQLite and keeps analytics strictly separate from optional "
            "live quote display. Use the pages in the left navigation for the screener, stock detail, "
            "and scan status views."
        )

    with storage.session_scope() as session:
        screener = storage.screener_dataframe(session, timeframe)
        latest_run = storage.latest_scan_run(session, timeframe)

    if latest_run is None:
        st.info("No scan has been run yet. Use the Run Scan button to populate the local database.")
        return

    metric1, metric2, metric3, metric4 = st.columns(4)
    metric1.metric("Last Scan Date", str(latest_run.scan_bar_date))
    metric2.metric("Stocks Processed", latest_run.stocks_processed)
    metric3.metric("Qualified Ranges", latest_run.ranges_detected)
    metric4.metric("Active Timeframe", latest_run.timeframe)

    if screener.empty:
        st.warning("The latest scan produced no qualified ranges.")
        return

    top_candidates = screener.head(10).copy()
    top_longs = screener[screener["setup_direction"] == "long"].head(10).copy()
    top_shorts = screener[screener["setup_direction"] == "short"].head(10).copy()

    st.subheader("Top Ranked Range Candidates")
    render_dataframe(
        top_candidates[
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
                "setup_direction",
            ]
        ]
    )

    left, right = st.columns(2)
    with left:
        st.subheader("Top Long Opportunities")
        render_dataframe(top_longs[["ticker", "range_score", "latest_close", "support_zone", "target_summary"]])
    with right:
        st.subheader("Top Short Opportunities")
        render_dataframe(top_shorts[["ticker", "range_score", "latest_close", "resistance_zone", "target_summary"]])


if __name__ == "__main__":
    main()
