"""Reusable chart rendering helpers."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.utils.charting import build_range_chart


def render_range_chart(frame: pd.DataFrame, detail: dict, live_price: float | None = None) -> None:
    figure = build_range_chart(frame, detail, live_price=live_price)
    st.plotly_chart(figure, use_container_width=True)
