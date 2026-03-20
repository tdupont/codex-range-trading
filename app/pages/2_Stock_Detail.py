"""Stock detail page."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.bootstrap import ensure_project_root_on_path

ensure_project_root_on_path(__file__)

import pandas as pd
import streamlit as st

from app.components.charts import render_range_chart
from app.components.metrics import render_score_metrics
from app.config.settings import settings
from app.services.scan_service import build_live_quote_provider
from app.services.storage_service import StorageService


storage = StorageService(settings)
storage.initialize_database()
live_quote_provider = build_live_quote_provider(settings)

st.title("Stock Detail")
st.caption("Detailed view of one qualified range candidate.")

timeframe = st.sidebar.selectbox("Timeframe", settings.supported_scan_timeframes, index=0)
with storage.session_scope() as session:
    tickers = storage.available_tickers(session, timeframe)

if not tickers:
    st.info("No qualified ranges available. Run a scan first.")
    st.stop()

ticker = st.sidebar.selectbox("Ticker", tickers)

with storage.session_scope() as session:
    detail = storage.latest_detail_context(session, ticker, timeframe)

if detail is None:
    st.warning("No detail available for the selected ticker.")
    st.stop()

stock = detail["stock"]
range_row = detail["range"]
indicator = detail["indicator"]
score = detail["score"]
setups = detail["setups"]
bars = detail["bars"]
live_quote = live_quote_provider.get_latest_quote(stock.ticker)

header_left, header_right = st.columns([2, 1])
with header_left:
    st.subheader(f"{stock.ticker} · {stock.name}")
    st.write(f"{stock.sector or 'Unknown sector'} | {stock.industry or 'Unknown industry'}")
with header_right:
    st.metric("Latest Quote", f"{live_quote.last_price:.2f}")
    st.caption(f"Display-only quote via {live_quote.provider} at {live_quote.quote_timestamp.isoformat()}")

if score is not None:
    render_score_metrics(score)

stats_col, setup_col = st.columns([1, 1])
with stats_col:
    st.subheader("Indicator Snapshot")
    st.write(
        {
            "ADX(14)": round(indicator.adx_14 or 0, 2) if indicator else None,
            "ATR(14)": round(indicator.atr_14 or 0, 2) if indicator else None,
            "RSI(14)": round(indicator.rsi_14 or 0, 2) if indicator else None,
            "Normalized SMA(20) Slope": round(indicator.normalized_sma_20_slope or 0, 4) if indicator else None,
            "Net Drift 30": round(indicator.net_drift_30 or 0, 2) if indicator else None,
        }
    )
    st.subheader("Range Geometry")
    st.write(
        {
            "Support Zone": f"{range_row.support_zone_low:.2f} - {range_row.support_zone_high:.2f}",
            "Resistance Zone": f"{range_row.resistance_zone_low:.2f} - {range_row.resistance_zone_high:.2f}",
            "Midline": round(range_row.midline, 2),
            "Support Touches": range_row.touch_count_support,
            "Resistance Touches": range_row.touch_count_resistance,
            "Containment Ratio": round(range_row.containment_ratio, 3),
            "Drift / Range": round(range_row.drift_to_range_ratio, 3),
            "Recent Breakout": range_row.has_recent_breakout,
        }
    )
with setup_col:
    st.subheader("Setup Explanation")
    for setup in setups:
        reward = abs(setup.target_2_price - ((setup.entry_low + setup.entry_high) / 2))
        risk = abs(setup.stop_price - ((setup.entry_low + setup.entry_high) / 2))
        rr = reward / risk if risk else None
        st.write(
            {
                "Direction": setup.setup_direction,
                "Status": setup.setup_status,
                "Entry Zone": f"{setup.entry_low:.2f} - {setup.entry_high:.2f}",
                "Stop": round(setup.stop_price, 2),
                "Target 1": round(setup.target_1_price, 2),
                "Target 2": round(setup.target_2_price, 2),
                "RSI": round(setup.rsi_14 or 0, 2) if setup.rsi_14 is not None else None,
                "Rejection Signal": setup.rejection_signal,
                "Risk/Reward To Target 2": round(rr, 2) if rr is not None else None,
            }
        )

chart_frame = pd.DataFrame(
    {
        "bar_date": [row.bar_date for row in bars],
        "open": [row.open for row in bars],
        "high": [row.high for row in bars],
        "low": [row.low for row in bars],
        "close": [row.close for row in bars],
    }
)
render_range_chart(chart_frame, detail, live_price=live_quote.last_price)

st.subheader("Recent Bars")
st.dataframe(chart_frame.tail(20), use_container_width=True, hide_index=True)
