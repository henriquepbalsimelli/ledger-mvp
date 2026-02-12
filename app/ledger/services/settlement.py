from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.core.exceptions import InvalidSettlementState, LockExceedsAvailable, SettleExceedsLocked
from app.ledger.models.settlement import Settlement
from app.ledger.repository.dominio_repository import DominioRepository
from app.ledger.repository.ledger_balance_repository import LedgerBalanceRepository
from app.ledger.repository.asset_repository import AssetRepository
from app.ledger.repository.ledger_event_repository import EventRepository
from app.ledger.repository.settlement_repository import SettlementRepository


class SettlementService:
    def __init__(self, db: Session, request: Request):
        self.db = db
        self.request = request

        self.balance_repository = LedgerBalanceRepository(db)
        self.dominio_repository = DominioRepository(db)
        self.settlement_repository = SettlementRepository(db)
        self.event_repository = EventRepository(db)
        self.asset_repository = AssetRepository(db)
        #
        # self.ledger_log_error = LedgerErrorLogger(__name__, request)
        # self.ledger_log = LedgerLogger(__name__, request)

    def create_settlement(self, account_id: int, asset: str, amount: Decimal):
        asset_row = self.asset_repository.get_or_create(asset)
        balance = self.balance_repository.get_balance_by_accont_id_for_update(account_id, asset_row.id)

        if balance.locked < amount:
            raise SettleExceedsLocked(
                message=f"locked={balance.locked} < amount={amount}",
                request=self.request,
                payload={
                    "account_id": account_id,
                    "asset": asset,
                    "amount": amount,
                },
            )

        pending_status = self.dominio_repository.get_status_by_name("PENDING")

        settlement = Settlement(
            account_id=account_id,
            id_asset=asset_row.id,
            amount=amount,
            id_status=pending_status.id,
        )

        self.db.add(settlement)
        return settlement

    def confirm_settlement(self, settlement_id: int):
        settlement = self.settlement_repository.get_settlement_for_update(settlement_id)

        if not settlement:
            raise HTTPException(detail=f"settlement {settlement_id} not found", status_code=404)

        if settlement.status != "SENT":
            raise InvalidSettlementState(
                message=f"Invalid settlement state: {settlement.status}",
                request=self.request,
                payload={
                    "settlement_id": settlement_id,
                    "current_status": settlement.status,
                },
            )

        balance = self.balance_repository.get_balance_by_accont_id_for_update(settlement.account_id, settlement.id_asset)

        balance.locked -= settlement.amount

        self.event_repository.create_event(
            idempotency_key=str(uuid4()),
            account_id=settlement.account_id,
            id_asset=settlement.id_asset,
            delta=-settlement.amount,
            event_type="settlement",
            reference_type="settlement_id",
            reference_id=str(settlement.id),
        )

        status_confirmed = self.dominio_repository.get_status_by_name("CONFIRMED")
        settlement.id_status = status_confirmed.id

        return settlement
