from decimal import Decimal, ROUND_DOWN

from sqlalchemy import text

from app.ledger.services.ledger import LedgerService
from tests.builders.account_builder import AccountBuilder
import uuid
from tests.conftest import TestingSessionLocal

def test_decimal_precision_and_event_sum(request_mock):
    session = TestingSessionLocal()
    service = LedgerService(session, request_mock)
    account = AccountBuilder(session, guid=uuid.uuid4()).build()
    asset = "USDC"
    account_id = account.id
    service.deposit(
        account_id=account_id,
        asset=asset,
        amount=Decimal("100.12345678"),
        idempotency_key="p1",
        reference_id="r1",
    )
    session.commit()
    from app.ledger import schemas

    service.lock_funds(
        payload=schemas.LockIn(
            account_id=account_id,
            asset=asset,
            amount=Decimal("30.12345678"),
            idempotency_key="p2",
            reference_id="r2",
        )
    )
    session.commit()
    # locked = 30.12345678, available = 70.00000000
    service.unlock_funds(
        idempotency_key="p3",
        account_id=account_id,
        asset=asset,
        amount=Decimal("10.00000001"),
        reference_id="r3",
    )
    session.commit()
    # locked = 20,12345677, available = 80.00000001
    service.withdraw(
        account_id=account_id,
        asset=asset,
        amount=Decimal("5.00000001"),
        idempotency_key="p4",
        reference_id="r4",
    )
    session.commit()

    balances = service.get_balances(account_id)[asset]
    total_balance = Decimal(balances["available"]) + Decimal(balances["locked"])

    # Lock e Unlock não alteram o saldo total
    events_sum = sum([Decimal(row[0]) for row in session.execute(text(f"""
        select delta 
        from event 
        where account_id = {account_id} 
        and event_type in ('deposit', 'withdraw')
    """))])

    assert total_balance == events_sum
    assert total_balance.as_tuple().exponent >= -8
    assert Decimal(balances["available"]).as_tuple().exponent >= -8
    assert Decimal(balances["locked"]).as_tuple().exponent >= -8
