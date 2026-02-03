from starlette.requests import Request

from app.core.ledger_logger import LedgerErrorLogger


class InsufficientFunds(Exception):
    def __init__(self, request: Request, payload, message="Insufficient funds" ):
        self.message = message
        super().__init__(self.message)

        self.ledger_log_error = LedgerErrorLogger(__name__, request)
        self.ledger_log_error.insufficient_funds(**payload)


class LockExceedsAvailable(Exception):
    def __init__(self, request: Request, payload, message="Lock exceeds available funds" ):
        self.message = message
        super().__init__(self.message)

        self.ledger_log_error = LedgerErrorLogger(__name__, request)
        self.ledger_log_error.lock_exceeds_available(**payload)


class UnlockExceedsLocked(Exception):
    def __init__(self, request: Request, payload, message="Unlock exceeds locked funds" ):
        self.message = message
        super().__init__(self.message)

        self.ledger_log_error = LedgerErrorLogger(__name__, request)
        self.ledger_log_error.unlock_exceeds_locked(**payload)