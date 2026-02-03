from pydantic import BaseModel, Field
from decimal import Decimal

class LockRequest(BaseModel):
    idempotency_key: str
    account_id: str
    asset: str
    amount: Decimal = Field(..., gt=0)
    reference_id: str

class UnlockRequest(LockRequest):
    pass