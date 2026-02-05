from decimal import Decimal

from pydantic import BaseModel


class WithdrawRequest(BaseModel):
    idempotency_key: str
    account_id: int
    asset: str
    amount: Decimal
    reference_id: str
