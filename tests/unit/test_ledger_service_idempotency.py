from decimal import Decimal

from app.ledger import schemas
from app.ledger.services.ledger import LedgerService
from tests.builders.account_builder import AccountBuilder


def _balance_snapshot(service, account_id, asset):
    bal = service.get_balances(account_id)[asset]
    return Decimal(bal["available"]), Decimal(bal["locked"])


def test_deposit_idempotent(db_session, request_mock):
    service = LedgerService(db_session, request_mock)
    account = AccountBuilder(db_session).build()

    key = "idemp-dep"
    service.deposit(
        account_id=account.id,
        asset="USDC",
        amount=Decimal("50"),
        idempotency_key=key,
        reference_id="ref-1",
    )
    db_session.commit()
    before = _balance_snapshot(service, account.id, "USDC")

    ev_again, _ = service.deposit(
        account_id=account.id,
        asset="USDC",
        amount=Decimal("999"),  # should be ignored
        idempotency_key=key,
        reference_id="ref-ignored",
    )
    db_session.commit()
    after = _balance_snapshot(service, account.id, "USDC")

    assert before == after
    assert ev_again.idempotency_key == key


def test_lock_idempotent(db_session, request_mock):
    service = LedgerService(db_session, request_mock)
    account = AccountBuilder(db_session).build()
    key = "idemp-lock"

    service.deposit(account_id=account.id, asset="USDC", amount=Decimal("100"), idempotency_key="dep", reference_id="r")
    db_session.commit()
    service.lock_funds(
        payload=schemas.LockIn(
            account_id=account.id,
            asset="USDC",
            amount=Decimal("30"),
            idempotency_key=key,
            reference_id="r1",
        )
    )
    db_session.commit()
    before = _balance_snapshot(service, account.id, "USDC")

    ev_again, _ = service.lock_funds(
        payload=schemas.LockIn(
            account_id=account.id,
            asset="USDC",
            amount=Decimal("5"),
            idempotency_key=key,
            reference_id="r1b",
        )
    )
    db_session.commit()
    after = _balance_snapshot(service, account.id, "USDC")

    assert before == after
    assert ev_again.idempotency_key == key


def test_unlock_idempotent(db_session, request_mock):
    service = LedgerService(db_session, request_mock)
    account = AccountBuilder(db_session).build()
    key = "idemp-unlock"

    service.deposit(
        account_id=account.id, asset="USDC", amount=Decimal("100"), idempotency_key="dep2", reference_id="r"
    )
    db_session.commit()
    service.lock_funds(
        payload=schemas.LockIn(
            account_id=account.id,
            asset="USDC",
            amount=Decimal("40"),
            idempotency_key="lock2",
            reference_id="r2",
        )
    )
    db_session.commit()
    before = _balance_snapshot(service, account.id, "USDC")

    ev_again, _ = service.unlock_funds(
        idempotency_key=key,
        account_id=account.id,
        asset="USDC",
        amount=Decimal("10"),
        reference_id="r3",
    )
    db_session.commit()
    after = _balance_snapshot(service, account.id, "USDC")
    # first unlock
    assert after[0] == before[0] + Decimal("10")
    assert after[1] == before[1] - Decimal("10")

    second_before = _balance_snapshot(service, account.id, "USDC")
    ev_same, _ = service.unlock_funds(
        idempotency_key=key,
        account_id=account.id,
        asset="USDC",
        amount=Decimal("999"),
        reference_id="r3b",
    )
    db_session.commit()
    second_after = _balance_snapshot(service, account.id, "USDC")

    assert second_before == second_after
    assert ev_same.idempotency_key == key


def test_withdraw_idempotent(db_session, request_mock):
    service = LedgerService(db_session, request_mock)
    account = AccountBuilder(db_session).build()
    key = "idemp-withdraw"

    service.deposit(
        account_id=account.id, asset="USDC", amount=Decimal("100"), idempotency_key="dep3", reference_id="r"
    )
    db_session.commit()
    before = _balance_snapshot(service, account.id, "USDC")

    service.withdraw(
        account_id=account.id,
        asset="USDC",
        amount=Decimal("25"),
        idempotency_key=key,
        reference_id="wd1",
    )
    db_session.commit()
    after = _balance_snapshot(service, account.id, "USDC")
    assert after[0] == before[0] - Decimal("25")

    ev_same, _ = service.withdraw(
        account_id=account.id,
        asset="USDC",
        amount=Decimal("999"),
        idempotency_key=key,
        reference_id="wd1b",
    )
    db_session.commit()
    final = _balance_snapshot(service, account.id, "USDC")

    assert final == after
    assert ev_same.idempotency_key == key
