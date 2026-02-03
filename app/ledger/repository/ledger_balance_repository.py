from app.ledger.models.ledger_balance import Balance
from sqlalchemy import select


class LedgerBalanceRepository:
    def __init__(self, db):
        self.db = db

    def get_balances_by_account_id(self, account_id: str):
        rows = self.db.execute(
            select(Balance).where(Balance.account_id == account_id)
        ).scalars().all()
        return rows

    def get_balance_by_account_id(self, account_id: str, asset: str):
        bal = self.db.execute(
            select(Balance).where(
                Balance.account_id == account_id,
                Balance.asset == asset,
            )
        ).scalar_one_or_none()

        return bal

    def update_balance(self, account_id, new_balance):
        query = """
        UPDATE ledger_balances
        SET balance = :new_balance
        WHERE account_id = :account_id
        """
        self.db.execute(query, {'new_balance': new_balance, 'account_id': account_id})

    def create_balance(self, account_id: str, asset: str, available: str = "0", locked: str = "0"):
        bal = Balance(account_id=account_id, asset=asset, available=available, locked=locked)
        self.db.add(bal)
        self.db.flush()
        return bal