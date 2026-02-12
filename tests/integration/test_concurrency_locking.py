import threading
import uuid
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.core.exceptions import LockExceedsAvailable
from app.ledger import schemas
from app.ledger.services.ledger import LedgerService
from tests.builders.account_builder import AccountBuilder
from tests.conftest import TestingSessionLocal


@pytest.mark.integration
def test_concurrent_locks_result_in_single_success(request_mock):
    # seed balance
    seed_session = TestingSessionLocal()
    guid = uuid.uuid4()
    account = AccountBuilder(seed_session, guid=guid).build()
    service = LedgerService(seed_session, request_mock)
    service.deposit(
        account_id=account.id,
        asset="USDC",
        amount=Decimal("100"),
        idempotency_key="seed-dep",
        reference_id="seed",
    )
    account_id = account.id
    seed_session.commit()
    seed_session.close()

    barrier = threading.Barrier(2)
    results = []

    def new_request():
        return SimpleNamespace(state=SimpleNamespace(request_id=f"req-{uuid.uuid4().hex[:8]}"))

    def lock_worker(key_suffix):
        session = TestingSessionLocal()
        svc = LedgerService(session, new_request())
        barrier.wait()
        try:
            svc.lock_funds(
                payload=schemas.LockIn(
                    account_id=account_id,
                    asset="USDC",
                    amount=Decimal("80"),
                    idempotency_key=f"lock-{key_suffix}",
                    reference_id=f"ref-{key_suffix}",
                )
            )
            session.commit()
            results.append("success")
        except LockExceedsAvailable:
            results.append("lock_exceeds")
        finally:
            session.close()

    t1 = threading.Thread(target=lock_worker, args=("a",))
    t2 = threading.Thread(target=lock_worker, args=("b",))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert sorted(results) == ["lock_exceeds", "success"]

    # Final balances should reflect exactly one lock of 80
    check_session = TestingSessionLocal()
    check_service = LedgerService(check_session, request_mock)
    bal = check_service.get_balances(account_id)["USDC"]
    assert Decimal(bal["locked"]) == Decimal("80")
    assert Decimal(bal["available"]) == Decimal("20")
    check_session.close()
