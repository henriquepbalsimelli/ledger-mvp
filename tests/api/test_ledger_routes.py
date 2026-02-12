import uuid
from decimal import Decimal

import pytest

from tests.builders.account_builder import AccountBuilder
from tests.conftest import TestingSessionLocal


@pytest.mark.api
def test_deposit_and_get_balances(client):
    session = TestingSessionLocal()
    account = AccountBuilder(session, guid=uuid.uuid4()).build()
    account_id = account.id
    session.close()

    payload = {
        "idempotency_key": "api-dep-1",
        "account_id": account_id,
        "asset": "USDC",
        "amount": "50.00",
        "reference_id": "r1",
    }
    resp = client.post("/ledger/deposit", json=payload)
    assert resp.status_code == 200

    balances = client.get(f"/ledger/balances?account_id={account_id}").json()["balances"]
    assert Decimal(str(balances["USDC"]["available"])) == Decimal("50.00")
    assert Decimal(str(balances["USDC"]["locked"])) == Decimal("0")


@pytest.mark.api
def test_withdraw_insufficient_returns_409(client):
    session = TestingSessionLocal()
    account = AccountBuilder(session, guid=uuid.uuid4()).build()
    account_id = account.id
    session.close()

    client.post(
        "/ledger/deposit",
        json={
            "idempotency_key": "api-dep-2",
            "account_id": account_id,
            "asset": "USDC",
            "amount": "10.00",
            "reference_id": "r2",
        },
    )

    resp = client.post(
        "/ledger/withdraw",
        json={
            "idempotency_key": "api-wd-2",
            "account_id": account_id,
            "asset": "USDC",
            "amount": "20.00",
            "reference_id": "r2b",
        },
    )
    assert resp.status_code == 409


@pytest.mark.api
def test_negative_amount_rejected_with_422(client):
    session = TestingSessionLocal()
    account = AccountBuilder(session, guid=uuid.uuid4()).build()
    account_id = account.id
    session.close()

    resp = client.post(
        "/ledger/lock",
        json={
            "idempotency_key": "api-lock-neg",
            "account_id": account_id,
            "asset": "USDC",
            "amount": "-5",
            "reference_id": "r3",
        },
    )
    assert resp.status_code == 422


@pytest.mark.api
def test_idempotent_retry_returns_same_balance(client):
    session = TestingSessionLocal()
    account = AccountBuilder(session, guid=uuid.uuid4()).build()
    account_id = account.id
    session.close()

    payload = {
        "idempotency_key": "api-dep-3",
        "account_id": account_id,
        "asset": "USDC",
        "amount": "30.00",
        "reference_id": "r4",
    }
    first = client.post("/ledger/deposit", json=payload)
    second = client.post("/ledger/deposit", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    balances = client.get(f"/ledger/balances?account_id={account_id}").json()["balances"]
    assert Decimal(str(balances["USDC"]["available"])) == Decimal("30.00")


@pytest.mark.api
def test_request_id_header_added(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert "X-Request-Id" in resp.headers
