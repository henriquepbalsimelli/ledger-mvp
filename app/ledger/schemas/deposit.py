from typing import Optional
from pydantic import BaseModel, Field
from decimal import Decimal

class DepositRequest(BaseModel):
    idempotency_key: str = Field(..., description="A unique key to ensure idempotency of the request")
    account_id: str = Field(..., description="The ID of the account to deposit funds into", examples=["3e6ab223-8094-4764-9e81-91574defe0a9"])
    asset: str = Field(..., description="The asset type to deposit (e.g., 'USD', 'BTC')", examples=["USD", "BTC"])
    amount: Decimal = Field(..., gt=0, description="The amount to deposit, must be greater than zero", examples=["100.00", "0.005"])
    reference_id: Optional[str] = Field(None, description="An optional reference ID for tracking purposes", examples=["dep_123456", "txn_654321"])