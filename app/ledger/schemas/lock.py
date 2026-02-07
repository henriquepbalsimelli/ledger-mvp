from decimal import Decimal

from pydantic import BaseModel, Field


class Unlock(BaseModel):
    idempotency_key: str
    account_id: int
    asset: str
    amount: Decimal = Field(..., gt=0)
    reference_id: str


class LockIn(BaseModel):
    idempotency_key: str
    account_id: int
    asset: str
    amount: Decimal = Field(..., gt=0)
    reference_id: str
