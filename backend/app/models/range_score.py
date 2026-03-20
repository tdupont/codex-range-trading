from __future__ import annotations

from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class RangeScore(TimestampMixin, Base):
    __tablename__ = "range_scores"
    __table_args__ = (
        UniqueConstraint("range_id", name="uq_range_scores_range_id"),
        Index("ix_range_scores_range_score_desc", "range_score"),
        Index("ix_range_scores_opportunity_score_desc", "opportunity_score"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    range_id: Mapped[int] = mapped_column(ForeignKey("ranges.id", ondelete="CASCADE"))
    range_score: Mapped[Decimal] = mapped_column(Numeric(6, 2))
    range_validity_score: Mapped[Decimal] = mapped_column(Numeric(6, 2))
    tradeability_score: Mapped[Decimal] = mapped_column(Numeric(6, 2))
    opportunity_score: Mapped[Decimal] = mapped_column(Numeric(6, 2))
    touch_quality_score: Mapped[Decimal] = mapped_column(Numeric(6, 2))
    trend_weakness_score: Mapped[Decimal] = mapped_column(Numeric(6, 2))
    containment_quality_score: Mapped[Decimal] = mapped_column(Numeric(6, 2))
    range_width_score: Mapped[Decimal] = mapped_column(Numeric(6, 2))
    liquidity_score: Mapped[Decimal] = mapped_column(Numeric(6, 2))
    current_opportunity_location_score: Mapped[Decimal] = mapped_column(Numeric(6, 2))
    scoring_version: Mapped[str] = mapped_column(String(32))

    range = relationship("RangeSnapshot", back_populates="score")
