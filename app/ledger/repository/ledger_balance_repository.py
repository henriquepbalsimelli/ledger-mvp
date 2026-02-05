from sqlalchemy import select

from app.ledger.models.ledger_balance import Balance


class LedgerBalanceRepository:
    def __init__(self, db):
        self.db = db

    def get_balances_by_account_id(self, account_id: str):
        rows = self.db.execute(select(Balance).where(Balance.account_id == account_id)).scalars().all()
        return rows

    def get_balance_by_account_id(self, account_id: str, asset: str):
        bal = self.db.execute(
            select(Balance).where(
                Balance.account_id == account_id,
                Balance.asset == asset,
            )
        ).scalar_one_or_none()

        return bal

    def create_balance(self, account_id: str, asset: str, available: str = "0", locked: str = "0"):
        bal = Balance(account_id=account_id, asset=asset, available=available, locked=locked)
        self.db.add(bal)
        self.db.flush()
        return bal
