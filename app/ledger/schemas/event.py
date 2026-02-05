from decimal import Decimal

from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    idempotency_key: str = Field(..., min_length=6, max_length=120)
    account_id: str = Field(examples=["3e6ab223-8094-4764-9e81-91574defe0a9"])
    asset: str = Field(examples=["USD", "BTC"])
    delta: Decimal = Field(..., examples=["100.00", "-0.005"])
    event_type: str = Field(examples=["deposit", "withdrawal", "transfer"])
    reference_type: str = Field(examples=["order", "invoice", "adjustment"])
    reference_id: str = Field(examples=["ord_123456", "inv_654321"])


class EventOut(BaseModel):
    idempotency_key: str
    account_id: str
    asset: str
    delta: Decimal
    event_type: str
    reference_type: str
    reference_id: str
