from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.ledger.repository.ledger_balance_repository import LedgerBalanceRepository
from app.ledger.repository.ledger_event_repository import EventRepository
from tests.builders.account_builder import AccountBuilder

import uuid
@pytest.mark.integration
def test_balance_unique_constraint(db_session):
    guid = uuid.uuid4()
    account = AccountBuilder(db_session, guid=guid).build()
    repo = LedgerBalanceRepository(db_session)

    repo.create_balance(account_id=account.id, asset="USDC", available=Decimal("0"), locked=Decimal("0"))
    with pytest.raises(IntegrityError):
        repo.create_balance(account_id=account.id, asset="USDC", available=Decimal("1"), locked=Decimal("0"))


@pytest.mark.integration
def test_event_idempotency_unique(db_session):
    account = AccountBuilder(db_session, guid=uuid.uuid4()).build()
    repo = EventRepository(db_session)

    repo.create_event(
        idempotency_key="dup-key",
        account_id=account.id,
        asset="USDC",
        delta=Decimal("1.23"),
        event_type="deposit",
        reference_type="deposit",
        reference_id="r1",
    )

    with pytest.raises(IntegrityError):
        repo.create_event(
            idempotency_key="dup-key",
            account_id=account.id,
            asset="USDC",
            delta=Decimal("2.34"),
            event_type="deposit",
            reference_type="deposit",
            reference_id="r2",
        )


@pytest.mark.integration
def test_event_persists_exact_delta(db_session):
    account = AccountBuilder(db_session, guid=uuid.uuid4()).build()
    repo = EventRepository(db_session)

    repo.create_event(
        idempotency_key="prec-1",
        account_id=account.id,
        asset="USDC",
        delta=Decimal("0.12345678"),
        event_type="deposit",
        reference_type="deposit",
        reference_id="r1",
    )
    db_session.flush()

    stored = repo.get_event_by_idempotency_key("prec-1")
    assert Decimal(stored.delta) == Decimal("0.12345678")
