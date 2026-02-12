from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ledger.models.event import LedgerEvent


class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_event_by_idempotency_key(self, idempotency_key: str):
        ev = self.db.execute(
            select(LedgerEvent).where(
                LedgerEvent.idempotency_key == idempotency_key,
            )
        ).scalar_one_or_none()

        return ev

    def create_event(
        self,
        idempotency_key: str,
        account_id: int,
        id_asset: int,
        delta: Decimal,
        event_type: str,
        reference_type: str,
        reference_id: str,
    ) -> LedgerEvent:
        ev = LedgerEvent(
            idempotency_key=idempotency_key,
            account_id=account_id,
            id_asset=id_asset,
            delta=delta,
            event_type=event_type,
            reference_type=reference_type,
            reference_id=reference_id,
        )
        self.db.add(ev)
        self.db.flush()
        return ev
