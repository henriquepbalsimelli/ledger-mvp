from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.ledger import schemas


def test_deposit_request_serialization():
    payload = {
        "idempotency_key": "abc12345",
        "account_id": 1,
        "asset": "USDC",
        "amount": "10.50",
        "reference_id": "ref-1",
    }
    model = schemas.DepositRequest(**payload)
    assert model.amount == Decimal("10.50")


def test_negative_amounts_rejected():
    with pytest.raises(ValidationError):
        schemas.WithdrawRequest(
            idempotency_key="wd-1", account_id=1, asset="USDC", amount=Decimal("-1"), reference_id="r"
        )
    with pytest.raises(ValidationError):
        schemas.LockIn(idempotency_key="lk-1", account_id=1, asset="USDC", amount=Decimal("0"), reference_id="r")


def test_event_idempotency_key_length():
    with pytest.raises(ValidationError):
        schemas.EventCreate(
            idempotency_key="short",
            account_id=1,
            asset="USDC",
            delta=Decimal("1"),
            event_type="deposit",
            reference_type="deposit",
            reference_id="r",
        )
