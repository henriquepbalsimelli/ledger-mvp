from fastapi import HTTPException
from starlette.requests import Request

from app.core.ledger_logger import LedgerErrorLogger
from app.ledger.schemas import request


class InsufficientFunds(HTTPException):
    def __init__(self, request: Request, payload, message="Insufficient funds"):
        self.message = message
        super().__init__(detail=self.message, status_code=409)

        self.ledger_log_error = LedgerErrorLogger(__name__, request)
        self.ledger_log_error.insufficient_funds(**payload)


class LockExceedsAvailable(HTTPException):
    def __init__(self, request: Request, payload, message="Lock exceeds available funds"):
        self.message = message
        super().__init__(detail=self.message, status_code=409)

        self.ledger_log_error = LedgerErrorLogger(__name__, request)
        self.ledger_log_error.lock_exceeds_available(**payload)


class UnlockExceedsLocked(HTTPException):
    def __init__(self, request: Request, payload, message="Unlock exceeds locked funds"):
        self.message = message
        super().__init__(detail=self.message, status_code=409)

        self.ledger_log_error = LedgerErrorLogger(__name__, request)
        self.ledger_log_error.unlock_exceeds_locked(**payload)


class SettleExceedsLocked(HTTPException):
    def __init__(self, request: Request, payload, message="Settle exceeds locked funds"):
        self.message = message
        super().__init__(detail=self.message, status_code=409)

        self.ledger_log_error = LedgerErrorLogger(__name__, request)
        self.ledger_log_error.settle_exceeds_locked(**payload)


class InvalidSettlementState(HTTPException):
    def __init__(self, request: Request, payload, message="Invalid settlement state"):
        self.message = message
        super().__init__(detail=self.message, status_code=409)

        self.ledger_log_error = LedgerErrorLogger(__name__, request)
        self.ledger_log_error.invalid_settlement_state(**payload)
