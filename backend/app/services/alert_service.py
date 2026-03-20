from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.constants import ALERT_TYPE_NEW_OPPORTUNITY, SETUP_STATUS_ACTIVE
from app.models import Alert, RangeScore, Stock, TradeSetup


class AlertService:
    def run(self, session: Session) -> list[Alert]:
        session.execute(delete(Alert))
        created: list[Alert] = []
        active_setups = list(
            session.scalars(select(TradeSetup).where(TradeSetup.status == SETUP_STATUS_ACTIVE).order_by(TradeSetup.id.asc()))
        )
        for setup in active_setups:
            stock = session.get(Stock, setup.stock_id)
            score = session.scalar(select(RangeScore).where(RangeScore.range_id == setup.range_id))
            if stock is None:
                continue
            alert = Alert(
                stock_id=setup.stock_id,
                range_id=setup.range_id,
                trade_setup_id=setup.id,
                alert_type=ALERT_TYPE_NEW_OPPORTUNITY,
                direction=setup.direction,
                message=f"{stock.ticker} entered {setup.direction} setup conditions on {setup.as_of_date}.",
                payload_json={
                    "ticker": stock.ticker,
                    "direction": setup.direction,
                    "range_score": float(score.range_score) if score else None,
                },
            )
            session.add(alert)
            created.append(alert)
        session.flush()
        return created
