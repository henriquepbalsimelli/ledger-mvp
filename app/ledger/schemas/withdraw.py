from decimal import Decimal

from pydantic import BaseModel, Field


class WithdrawRequest(BaseModel):
    idempotency_key: str
    account_id: int
    asset: str
    amount: Decimal = Field(..., gt=0)
    reference_id: str
