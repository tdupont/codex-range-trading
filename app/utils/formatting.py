"""Formatting helpers for UI rendering."""

from __future__ import annotations


def format_price(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:.2f}"


def format_score(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:.1f}"
