"""Reusable metric display helpers."""

from __future__ import annotations

import streamlit as st

from app.utils.formatting import format_score


def render_score_metrics(score) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Range Score", format_score(score.range_score))
    col2.metric("Range Validity", format_score(score.range_validity_score))
    col3.metric("Tradeability", format_score(score.tradeability_score))
    col4.metric("Opportunity", format_score(score.opportunity_score))
