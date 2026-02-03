from decimal import Decimal

from pydantic import BaseModel

class Unlock(BaseModel):
    idempotency_key: str
    account_id: str
    asset: str
    amount: Decimal
    reference_id: str

class LockIn(BaseModel):
    idempotency_key: str
    account_id: str
    asset: str
    amount: Decimal
    reference_id: str