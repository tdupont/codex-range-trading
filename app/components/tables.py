"""Reusable table helpers."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def render_dataframe(frame: pd.DataFrame, *, height: int = 420) -> None:
    st.dataframe(frame, use_container_width=True, height=height, hide_index=True)
