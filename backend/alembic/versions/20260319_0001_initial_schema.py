"""initial schema

Revision ID: 20260319_0001
Revises: None
Create Date: 2026-03-19 00:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260319_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "stocks",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("ticker", sa.String(length=16), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("exchange", sa.String(length=32), nullable=True),
        sa.Column("sector", sa.String(length=128), nullable=True),
        sa.Column("industry", sa.String(length=128), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("universe", sa.String(length=32), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("ticker", name="uq_stocks_ticker"),
    )
    op.create_index("ix_stocks_universe_is_active", "stocks", ["universe", "is_active"])

    op.create_table(
        "ohlcv",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("stock_id", sa.BigInteger(), sa.ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("trade_date", sa.Date(), nullable=False),
        sa.Column("open", sa.Numeric(18, 6), nullable=False),
        sa.Column("high", sa.Numeric(18, 6), nullable=False),
        sa.Column("low", sa.Numeric(18, 6), nullable=False),
        sa.Column("close", sa.Numeric(18, 6), nullable=False),
        sa.Column("adjusted_close", sa.Numeric(18, 6), nullable=True),
        sa.Column("volume", sa.BigInteger(), nullable=False),
        sa.Column("vwap", sa.Numeric(18, 6), nullable=True),
        sa.Column("data_source", sa.String(length=64), nullable=False),
        sa.Column("is_adjusted_series", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("stock_id", "trade_date", name="uq_ohlcv_stock_trade_date"),
    )
    op.create_index("ix_ohlcv_trade_date", "ohlcv", ["trade_date"])
    op.create_index("ix_ohlcv_stock_trade_date_desc", "ohlcv", ["stock_id", "trade_date"])

    op.create_table(
        "indicators",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("stock_id", sa.BigInteger(), sa.ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("trade_date", sa.Date(), nullable=False),
        sa.Column("sma_20", sa.Numeric(18, 6), nullable=True),
        sa.Column("sma_20_slope", sa.Numeric(18, 6), nullable=True),
        sa.Column("atr_14", sa.Numeric(18, 6), nullable=True),
        sa.Column("adx_14", sa.Numeric(18, 6), nullable=True),
        sa.Column("rsi_14", sa.Numeric(18, 6), nullable=True),
        sa.Column("avg_dollar_volume_20", sa.Numeric(18, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("stock_id", "trade_date", name="uq_indicators_stock_trade_date"),
    )
    op.create_index("ix_indicators_trade_date", "indicators", ["trade_date"])
    op.create_index("ix_indicators_stock_trade_date_desc", "indicators", ["stock_id", "trade_date"])

    op.create_table(
        "ranges",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("stock_id", sa.BigInteger(), sa.ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("as_of_date", sa.Date(), nullable=False),
        sa.Column("lookback_days", sa.Integer(), nullable=False),
        sa.Column("upper_bound", sa.Numeric(18, 6), nullable=False),
        sa.Column("lower_bound", sa.Numeric(18, 6), nullable=False),
        sa.Column("midline", sa.Numeric(18, 6), nullable=False),
        sa.Column("range_width", sa.Numeric(18, 6), nullable=False),
        sa.Column("range_width_atr_multiple", sa.Numeric(18, 6), nullable=False),
        sa.Column("support_zone_low", sa.Numeric(18, 6), nullable=False),
        sa.Column("support_zone_high", sa.Numeric(18, 6), nullable=False),
        sa.Column("resistance_zone_low", sa.Numeric(18, 6), nullable=False),
        sa.Column("resistance_zone_high", sa.Numeric(18, 6), nullable=False),
        sa.Column("containment_ratio", sa.Numeric(8, 6), nullable=False),
        sa.Column("support_touch_count", sa.Integer(), nullable=False),
        sa.Column("resistance_touch_count", sa.Integer(), nullable=False),
        sa.Column("latest_close", sa.Numeric(18, 6), nullable=False),
        sa.Column("qualified", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notes_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("stock_id", "as_of_date", name="uq_ranges_stock_as_of_date"),
    )
    op.create_index("ix_ranges_as_of_date_desc", "ranges", ["as_of_date"])
    op.create_index("ix_ranges_qualified_as_of_date_desc", "ranges", ["qualified", "as_of_date"])

    op.create_table(
        "range_scores",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("range_id", sa.BigInteger(), sa.ForeignKey("ranges.id", ondelete="CASCADE"), nullable=False),
        sa.Column("range_score", sa.Numeric(6, 2), nullable=False),
        sa.Column("range_validity_score", sa.Numeric(6, 2), nullable=False),
        sa.Column("tradeability_score", sa.Numeric(6, 2), nullable=False),
        sa.Column("opportunity_score", sa.Numeric(6, 2), nullable=False),
        sa.Column("touch_quality_score", sa.Numeric(6, 2), nullable=False),
        sa.Column("trend_weakness_score", sa.Numeric(6, 2), nullable=False),
        sa.Column("containment_quality_score", sa.Numeric(6, 2), nullable=False),
        sa.Column("range_width_score", sa.Numeric(6, 2), nullable=False),
        sa.Column("liquidity_score", sa.Numeric(6, 2), nullable=False),
        sa.Column("current_opportunity_location_score", sa.Numeric(6, 2), nullable=False),
        sa.Column("scoring_version", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("range_id", name="uq_range_scores_range_id"),
    )
    op.create_index("ix_range_scores_range_score_desc", "range_scores", ["range_score"])
    op.create_index("ix_range_scores_opportunity_score_desc", "range_scores", ["opportunity_score"])

    op.create_table(
        "trade_setups",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("range_id", sa.BigInteger(), sa.ForeignKey("ranges.id", ondelete="CASCADE"), nullable=False),
        sa.Column("stock_id", sa.BigInteger(), sa.ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("as_of_date", sa.Date(), nullable=False),
        sa.Column("direction", sa.String(length=8), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("entry_zone_low", sa.Numeric(18, 6), nullable=False),
        sa.Column("entry_zone_high", sa.Numeric(18, 6), nullable=False),
        sa.Column("stop_price", sa.Numeric(18, 6), nullable=False),
        sa.Column("target_1_price", sa.Numeric(18, 6), nullable=False),
        sa.Column("target_2_price", sa.Numeric(18, 6), nullable=False),
        sa.Column("rejection_signal", sa.String(length=64), nullable=True),
        sa.Column("latest_close", sa.Numeric(18, 6), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("range_id", "direction", name="uq_trade_setups_range_id_direction"),
    )
    op.create_index("ix_trade_setups_as_of_date_status", "trade_setups", ["as_of_date", "status"])
    op.create_index("ix_trade_setups_stock_as_of_date_desc", "trade_setups", ["stock_id", "as_of_date"])

    op.create_table(
        "alerts",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("stock_id", sa.BigInteger(), sa.ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("range_id", sa.BigInteger(), sa.ForeignKey("ranges.id", ondelete="SET NULL"), nullable=True),
        sa.Column("trade_setup_id", sa.BigInteger(), sa.ForeignKey("trade_setups.id", ondelete="SET NULL"), nullable=True),
        sa.Column("alert_type", sa.String(length=32), nullable=False),
        sa.Column("direction", sa.String(length=8), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_alerts_created_at_desc", "alerts", ["created_at"])
    op.create_index("ix_alerts_stock_created_at_desc", "alerts", ["stock_id", "created_at"])
    op.create_index("ix_alerts_alert_type_created_at_desc", "alerts", ["alert_type", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_alerts_alert_type_created_at_desc", table_name="alerts")
    op.drop_index("ix_alerts_stock_created_at_desc", table_name="alerts")
    op.drop_index("ix_alerts_created_at_desc", table_name="alerts")
    op.drop_table("alerts")
    op.drop_index("ix_trade_setups_stock_as_of_date_desc", table_name="trade_setups")
    op.drop_index("ix_trade_setups_as_of_date_status", table_name="trade_setups")
    op.drop_table("trade_setups")
    op.drop_index("ix_range_scores_opportunity_score_desc", table_name="range_scores")
    op.drop_index("ix_range_scores_range_score_desc", table_name="range_scores")
    op.drop_table("range_scores")
    op.drop_index("ix_ranges_qualified_as_of_date_desc", table_name="ranges")
    op.drop_index("ix_ranges_as_of_date_desc", table_name="ranges")
    op.drop_table("ranges")
    op.drop_index("ix_indicators_stock_trade_date_desc", table_name="indicators")
    op.drop_index("ix_indicators_trade_date", table_name="indicators")
    op.drop_table("indicators")
    op.drop_index("ix_ohlcv_stock_trade_date_desc", table_name="ohlcv")
    op.drop_index("ix_ohlcv_trade_date", table_name="ohlcv")
    op.drop_table("ohlcv")
    op.drop_index("ix_stocks_universe_is_active", table_name="stocks")
    op.drop_table("stocks")
