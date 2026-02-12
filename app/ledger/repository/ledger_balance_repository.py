from sqlalchemy import select
from sqlalchemy.orm import noload

from app.ledger.models.balance import Balance


class LedgerBalanceRepository:
    def __init__(self, db):
        self.db = db

    def get_balances_by_account_id(self, account_id: int):
        rows = self.db.execute(select(Balance).where(Balance.account_id == account_id)).scalars().all()
        return rows

    def get_balance_by_account_id(self, account_id: int, id_asset: int):
        bal = self.db.execute(
            select(Balance).where(
                Balance.account_id == account_id,
                Balance.id_asset == id_asset,
            )
        ).scalar_one_or_none()

        return bal

    def get_balance_by_accont_id_for_update(self, account_id: int, id_asset: int):
        bal = self.db.execute(
            select(Balance)
            .options(noload("*"))
            .where(
                Balance.account_id == account_id,
                Balance.id_asset == id_asset,
            )
            .with_for_update(of=Balance)
        ).scalar_one_or_none()

        return bal

    def create_balance(self, account_id: int, id_asset: int, available: str = "0", locked: str = "0"):
        bal = Balance(account_id=account_id, id_asset=id_asset, available=available, locked=locked)
        self.db.add(bal)
        self.db.flush()
        return bal
