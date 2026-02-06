from decimal import Decimal

from sqlalchemy.orm import Session
from starlette.requests import Request

from app.core.exceptions import InsufficientFunds, LockExceedsAvailable, UnlockExceedsLocked
from app.core.ledger_logger import LedgerErrorLogger, LedgerLogger
from app.ledger import schemas
from app.ledger.models.balance import Balance
from app.ledger.repository.ledger_balance_repository import LedgerBalanceRepository
from app.ledger.repository.ledger_event_repository import EventRepository


class LedgerService:
    def __init__(self, db: Session, request: Request):
        self.db = db
        self.request = request

        self.balance_repository = LedgerBalanceRepository(db)
        self.event_repository = EventRepository(db)

        self.ledger_log_error = LedgerErrorLogger(__name__, request)
        self.ledger_log = LedgerLogger(__name__, request)

    def get_balances(self, account_id: int):
        rows = self.balance_repository.get_balances_by_account_id(account_id)
        balances = {
            r.asset: {
                "available": Decimal(r.available),
                "locked": Decimal(r.locked),
            }
            for r in rows
        }
        return balances

    def _get_or_create_balance(self, account_id: int, asset: str) -> Balance:
        bal = self.balance_repository.get_balance_by_account_id(account_id, asset)

        if bal:
            return bal
        bal = self.balance_repository.create_balance(account_id, asset, Decimal("0"), Decimal("0"))
        return bal

    def deposit(self, *, idempotency_key: str, account_id: int, asset: str, amount: Decimal, reference_id: str):
        bal = self._get_or_create_balance(account_id, asset)
        existing_event = self.event_repository.get_event_by_idempotency_key(idempotency_key)
        if existing_event:
            self.ledger_log_error.event_exists(
                **{
                    "account_id": account_id,
                    "asset": asset,
                    "amount": amount,
                    "idempotency_key": idempotency_key,
                    "operation": "deposit",
                }
            )
            return existing_event, bal

        self.ledger_log.deposit(
            **{
                "account_id": account_id,
                "asset": asset,
                "amount": amount,
                "idempotency_key": idempotency_key,
            }
        )

        ev = self.event_repository.create_event(
            idempotency_key=idempotency_key,
            account_id=account_id,
            asset=asset,
            delta=amount,
            event_type="deposit",
            reference_type="deposit",
            reference_id=reference_id,
        )
        bal.available = Decimal(bal.available) + amount
        self.db.flush()
        return ev, bal

    def lock_funds(self, payload: schemas.LockIn):
        self.ledger_log.lock(
            **{
                **payload.model_dump(),
            }
        )

        bal = self._get_or_create_balance(payload.account_id, payload.asset)
        existing_event = self.event_repository.get_event_by_idempotency_key(payload.idempotency_key)
        if existing_event:
            self.ledger_log_error.event_exists(**payload.model_dump())
            return existing_event, bal

        if Decimal(bal.available) < payload.amount:
            raise LockExceedsAvailable(
                message=f"available={bal.available} < amount={payload.amount}",
                request=self.request,
                payload=payload.model_dump(),
            )

        ev = self.event_repository.create_event(
            idempotency_key=payload.idempotency_key,
            account_id=payload.account_id,
            asset=payload.asset,
            delta=-payload.amount,
            reference_id=payload.reference_id,
            event_type="lock",
            reference_type="payment",
        )

        bal.available = Decimal(bal.available) - payload.amount
        bal.locked = Decimal(bal.locked) + payload.amount
        self.db.flush()
        return ev, bal

    def unlock_funds(self, *, idempotency_key: str, account_id: int, asset: str, amount: Decimal, reference_id: str):
        existing = self.event_repository.get_event_by_idempotency_key(idempotency_key)
        bal = self._get_or_create_balance(account_id, asset)
        if existing:
            return existing, bal

        if Decimal(bal.locked) < amount:
            raise UnlockExceedsLocked(
                message=f"locked={bal.locked} < amount={amount}",
                request=self.request,
                payload={
                    "account_id": account_id,
                    "asset": asset,
                    "amount": amount,
                    "idempotency_key": idempotency_key,
                },
            )

        ev = self.event_repository.create_event(
            idempotency_key=idempotency_key,
            account_id=account_id,
            asset=asset,
            delta=amount,
            event_type="unlock",
            reference_type="payment",
            reference_id=reference_id,
        )

        bal.locked = Decimal(bal.locked) - amount
        bal.available = Decimal(bal.available) + amount
        return ev, bal

    def withdraw(
        self,
        *,
        idempotency_key: str,
        account_id: int,
        asset: str,
        amount: Decimal,
        reference_id: str,
    ):
        if amount <= 0:
            raise ValueError("Withdraw amount must be positive")

        bal = self._get_or_create_balance(account_id, asset)
        existing = self.event_repository.get_event_by_idempotency_key(idempotency_key)
        if existing:
            self.ledger_log_error.event_exists(
                **{
                    "account_id": account_id,
                    "asset": asset,
                    "amount": amount,
                    "idempotency_key": idempotency_key,
                    "operation": "withdraw",
                }
            )
            return existing, bal

        if bal.available < amount:
            raise InsufficientFunds(
                request=self.request,
                message=f"available={bal.available}, requested={amount}",
                payload={
                    "account_id": account_id,
                    "asset": asset,
                    "amount": amount,
                    "idempotency_key": idempotency_key,
                },
            )

        ev = self.event_repository.create_event(
            idempotency_key=idempotency_key,
            account_id=account_id,
            asset=asset,
            delta=-amount,
            event_type="withdraw",
            reference_type="withdraw",
            reference_id=reference_id,
        )

        bal.available -= amount

        return ev, bal
