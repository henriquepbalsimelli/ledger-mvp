from fastapi import HTTPException
from starlette.requests import Request

from app.core.ledger_logger import LedgerErrorLogger


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
