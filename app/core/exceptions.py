from starlette.requests import Request

from app.core.ledger_logger import LedgerErrorLogger


class InsufficientFunds(Exception):
    def __init__(self, request: Request, payload, message="Insufficient funds" ):
        self.message = message
        super().__init__(self.message)

        self.ledger_log_error = LedgerErrorLogger(__name__, request)
        self.ledger_log_error.insufficient_funds(**payload)
