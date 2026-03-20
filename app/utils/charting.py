"""Plotly chart helpers."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go


def build_range_chart(frame: pd.DataFrame, detail: dict, live_price: float | None = None) -> go.Figure:
    range_row = detail["range"]
    setups = detail["setups"]
    figure = go.Figure()
    figure.add_trace(
        go.Candlestick(
            x=frame["bar_date"],
            open=frame["open"],
            high=frame["high"],
            low=frame["low"],
            close=frame["close"],
            name="OHLC",
        )
    )

    figure.add_hrect(
        y0=range_row.support_zone_low,
        y1=range_row.support_zone_high,
        fillcolor="rgba(46, 125, 50, 0.18)",
        line_width=0,
        annotation_text="Support zone",
    )
    figure.add_hrect(
        y0=range_row.resistance_zone_low,
        y1=range_row.resistance_zone_high,
        fillcolor="rgba(198, 40, 40, 0.18)",
        line_width=0,
        annotation_text="Resistance zone",
    )
    figure.add_hline(y=range_row.midline, line_dash="dash", line_color="#455a64", annotation_text="Midline")

    for setup in setups:
        color = "#2e7d32" if setup.setup_direction == "long" else "#c62828"
        figure.add_hrect(
            y0=setup.entry_low,
            y1=setup.entry_high,
            fillcolor="rgba(2, 136, 209, 0.10)",
            line_width=0,
        )
        figure.add_hline(y=setup.stop_price, line_color=color, line_dash="dot")
        figure.add_hline(y=setup.target_1_price, line_color="#1565c0", line_dash="dash")
        figure.add_hline(y=setup.target_2_price, line_color="#6a1b9a", line_dash="dash")

    if live_price is not None:
        figure.add_trace(
            go.Scatter(
                x=[frame["bar_date"].iloc[-1]],
                y=[live_price],
                mode="markers",
                marker={"size": 12, "color": "#ffb300"},
                name="Latest quote",
            )
        )

    figure.update_layout(
        height=620,
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
        xaxis_rangeslider_visible=False,
        legend_orientation="h",
    )
    return figure
