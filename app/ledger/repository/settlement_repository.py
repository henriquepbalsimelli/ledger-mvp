from app.ledger.models import Settlement


class SettlementRepository:
    def __init__(self, db):
        self.db = db

    def get_settlement_for_update(self, settlement_id: int) -> Settlement | None:
        return self.db.query(Settlement).filter(Settlement.id == settlement_id).with_for_update().first()
