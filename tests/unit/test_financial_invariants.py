from decimal import Decimal
import pytest

from app.ledger.services.ledger import LedgerService
from app.core.exceptions import (
    InsufficientFunds,
    LockExceedsAvailable,
    UnlockExceedsLocked,
)

class TestFinancialInvariants:
    def test_available_and_locked_never_negative(
        self, db_session
    ):
        service = LedgerService(db_session)

        service.deposit(
            account_id="acc-1",
            asset="USDC",
            amount=Decimal("100"),
            idempotency_key="dep-1",
            request_id="req-1",
        )

        service.lock(
            account_id="acc-1",
            asset="USDC",
            amount=Decimal("40"),
            idempotency_key="lock-1",
            request_id="req-1",
        )

        balance = service.get_balance("acc-1", "USDC")

        assert balance.available >= 0
        assert balance.locked >= 0
        assert balance.available + balance.locked >= 0

    def test_lock_does_not_create_or_destroy_money(
        self, db_session
    ):
        service = LedgerService(db_session)

        service.deposit(
            account_id="acc-2",
            asset="USDC",
            amount=Decimal("100"),
            idempotency_key="dep-2",
            request_id="req-2",
        )

        before = service.get_balance("acc-2", "USDC")

        service.lock(
            account_id="acc-2",
            asset="USDC",
            amount=Decimal("30"),
            idempotency_key="lock-2",
            request_id="req-2",
        )

        after = service.get_balance("acc-2", "USDC")

        assert before.available + before.locked == after.available + after.locked

    def test_unlock_does_not_create_or_destroy_money(
        self, db_session
    ):
        service = LedgerService(db_session)

        service.deposit(
            account_id="acc-3",
            asset="USDC",
            amount=Decimal("100"),
            idempotency_key="dep-3",
            request_id="req-3",
        )

        service.lock(
            account_id="acc-3",
            asset="USDC",
            amount=Decimal("50"),
            idempotency_key="lock-3",
            request_id="req-3",
        )

        before = service.get_balance("acc-3", "USDC")

        service.unlock(
            account_id="acc-3",
            asset="USDC",
            amount=Decimal("20"),
            idempotency_key="unlock-3",
            request_id="req-3",
        )

        after = service.get_balance("acc-3", "USDC")

        assert before.available + before.locked == after.available + after.locked

    def test_withdraw_reduces_total_balance(
        self, db_session
    ):
        service = LedgerService(db_session)

        service.deposit(
            account_id="acc-4",
            asset="USDC",
            amount=Decimal("100"),
            idempotency_key="dep-4",
            request_id="req-4",
        )

        before = service.get_balance("acc-4", "USDC")

        service.withdraw(
            account_id="acc-4",
            asset="USDC",
            amount=Decimal("30"),
            idempotency_key="wd-4",
            request_id="req-4",
        )

        after = service.get_balance("acc-4", "USDC")

        assert after.available + after.locked == before.available + before.locked - Decimal("30")

    def test_lock_more_than_available_raises_error(
        self, db_session
    ):
        service = LedgerService(db_session)

        service.deposit(
            account_id="acc-5",
            asset="USDC",
            amount=Decimal("20"),
            idempotency_key="dep-5",
            request_id="req-5",
        )

        with pytest.raises(LockExceedsAvailable):
            service.lock(
                account_id="acc-5",
                asset="USDC",
                amount=Decimal("50"),
                idempotency_key="lock-5",
                request_id="req-5",
            )

    def test_unlock_more_than_locked_raises_error(
        self, db_session
    ):
        service = LedgerService(db_session)

        service.deposit(
            account_id="acc-6",
            asset="USDC",
            amount=Decimal("100"),
            idempotency_key="dep-6",
            request_id="req-6",
        )

        service.lock(
            account_id="acc-6",
            asset="USDC",
            amount=Decimal("40"),
            idempotency_key="lock-6",
            request_id="req-6",
        )

        with pytest.raises(UnlockExceedsLocked):
            service.unlock(
                account_id="acc-6",
                asset="USDC",
                amount=Decimal("60"),
                idempotency_key="unlock-6",
                request_id="req-6",
            )

    def test_withdraw_more_than_available_raises_error(
        self, db_session
    ):
        service = LedgerService(db_session)

        service.deposit(
            account_id="acc-7",
            asset="USDC",
            amount=Decimal("30"),
            idempotency_key="dep-7",
            request_id="req-7",
        )

        with pytest.raises(InsufficientFunds):
            service.withdraw(
                account_id="acc-7",
                asset="USDC",
                amount=Decimal("50"),
                idempotency_key="wd-7",
                request_id="req-7",
            )