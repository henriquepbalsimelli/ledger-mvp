from decimal import Decimal

import pytest

from app.core.exceptions import InsufficientFunds, LockExceedsAvailable, UnlockExceedsLocked
from app.ledger import schemas
from app.ledger.services.ledger import LedgerService
from tests.builders.account_builder import AccountBuilder


class TestFinancialInvariants:
    def test_available_and_locked_never_negative(self, db_session, request_mock):
        service = LedgerService(db=db_session, request=request_mock)

        account = AccountBuilder(db_session).build()

        asset = "USDC"
        service.deposit(
            account_id=account.id,
            asset=asset,
            amount=Decimal("100"),
            idempotency_key="dep-1",
            reference_id="ref-1",
        )

        payload = schemas.LockIn(
            account_id=account.id,
            asset=asset,
            amount=Decimal("20"),
            idempotency_key="lock-1",
            reference_id="ref-1",
        )

        service.lock_funds(payload)

        balance = service.get_balances(account.id)

        assert balance[asset]["available"] >= 0
        assert balance[asset]["locked"] >= 0
        assert balance[asset]["available"] + balance[asset]["locked"] >= 0

    def test_lock_does_not_create_or_destroy_money(self, db_session, request_mock):
        service = LedgerService(db=db_session, request=request_mock)
        asset = "USDC"
        account = AccountBuilder(db_session).build()
        service.deposit(
            account_id=account.id,
            asset=asset,
            amount=Decimal("100"),
            idempotency_key="dep-2",
            reference_id="ref-2",
        )

        before = service.get_balances(account.id)

        payload = schemas.LockIn(
            account_id=account.id,
            asset=asset,
            amount=Decimal("30"),
            idempotency_key="lock-2",
            reference_id="ref-2",
        )
        service.lock_funds(payload)

        after = service.get_balances(account.id)

        assert (
            before[asset]["available"] + before[asset]["locked"] == after[asset]["available"] + after[asset]["locked"]
        )

    def test_unlock_does_not_create_or_destroy_money(self, db_session, request_mock):
        service = LedgerService(db=db_session, request=request_mock)
        account = AccountBuilder(db_session).build()
        asset = "USDC"
        service.deposit(
            account_id=account.id,
            asset=asset,
            amount=Decimal("100"),
            idempotency_key="dep-3",
            reference_id="ref-3",
        )

        payload = schemas.LockIn(
            account_id=account.id,
            asset=asset,
            amount=Decimal("50"),
            idempotency_key="lock-3",
            reference_id="ref-3",
        )
        service.lock_funds(payload)

        before = service.get_balances(account.id)

        service.unlock_funds(
            account_id=account.id,
            asset="USDC",
            amount=Decimal("20"),
            idempotency_key="unlock-3",
            reference_id="ref-unlock-3",
        )

        after = service.get_balances(account.id)

        assert (
            before[asset]["available"] + before[asset]["locked"] == after[asset]["available"] + after[asset]["locked"]
        )

    def test_withdraw_reduces_total_balance(self, db_session, request_mock):
        service = LedgerService(db=db_session, request=request_mock)
        asset = "USDC"
        account = AccountBuilder(db_session).build()
        service.deposit(
            account_id=account.id,
            asset=asset,
            amount=Decimal("100"),
            idempotency_key="dep-4",
            reference_id="ref-4",
        )

        before = service.get_balances(account.id)

        service.withdraw(
            account_id=account.id,
            asset=asset,
            amount=Decimal("30"),
            idempotency_key="wd-4",
            reference_id="ref-wd-4",
        )

        after = service.get_balances(account.id)

        assert after[asset]["available"] >= 0
        assert after[asset]["locked"] >= 0
        assert after[asset]["available"] + after[asset]["locked"] == before[asset]["available"] + before[asset][
            "locked"
        ] - Decimal("30")

    def test_lock_more_than_available_raises_error(self, db_session, request_mock):
        service = LedgerService(db_session, request_mock)
        asset = "USDC"
        account = AccountBuilder(db_session).build()
        service.deposit(
            account_id=account.id,
            asset=asset,
            amount=Decimal("20"),
            idempotency_key="dep-5",
            reference_id="ref-5",
        )

        with pytest.raises(LockExceedsAvailable):
            payload = schemas.LockIn(
                account_id=account.id,
                asset=asset,
                amount=Decimal("30"),
                idempotency_key="lock-5",
                reference_id="ref-5",
            )
            service.lock_funds(payload)

    def test_unlock_more_than_locked_raises_error(self, db_session, request_mock):
        service = LedgerService(db_session, request_mock)
        asset = "USDC"
        account = AccountBuilder(db_session).build()
        service.deposit(
            account_id=account.id,
            asset=asset,
            amount=Decimal("100"),
            idempotency_key="dep-6",
            reference_id="ref-6",
        )

        service.lock_funds(
            schemas.LockIn(
                account_id=account.id,
                asset=asset,
                amount=Decimal("50"),
                idempotency_key="lock-6",
                reference_id="ref-6",
            )
        )

        with pytest.raises(UnlockExceedsLocked):
            service.unlock_funds(
                account_id=account.id,
                asset=asset,
                amount=Decimal("60"),
                idempotency_key="unlock-6",
                reference_id="ref-unlock-6",
            )

    def test_withdraw_more_than_available_raises_error(self, db_session, request_mock):
        service = LedgerService(db_session, request_mock)
        account = AccountBuilder(db_session).build()
        service.deposit(
            account_id=account.id,
            asset="USDC",
            amount=Decimal("30"),
            idempotency_key="dep-7",
            reference_id="ref-7",
        )

        with pytest.raises(InsufficientFunds):
            service.withdraw(
                account_id=account.id,
                asset="USDC",
                amount=Decimal("50"),
                idempotency_key="wd-7",
                reference_id="ref-wd-7",
            )

    def test_withdraw_considers_locked_balance(self, db_session, request_mock):
        service = LedgerService(db_session, request_mock)
        account = AccountBuilder(db_session).build()
        asset = "USDC"
        service.deposit(
            account_id=account.id,
            asset=asset,
            amount=Decimal("100"),
            idempotency_key="dep-8",
            reference_id="ref-8",
        )

        service.lock_funds(
            schemas.LockIn(
                account_id=account.id,
                asset=asset,
                amount=Decimal("80"),
                idempotency_key="lock-8",
                reference_id="ref-8",
            )
        )

        with pytest.raises(InsufficientFunds):
            service.withdraw(
                account_id=account.id,
                asset=asset,
                amount=Decimal("30"),
                idempotency_key="wd-8",
                reference_id="ref-wd-8",
            )
