from decimal import ROUND_DOWN, Decimal

import pytest
from hypothesis import Phase, settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule, run_state_machine_as_test
from sqlalchemy import text

from app.ledger import schemas
from app.ledger.services.ledger import LedgerService
from tests.builders.account_builder import AccountBuilder
from tests.conftest import TestingSessionLocal, engine


class LedgerStateMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        # each run uses isolated transaction
        self.connection = engine.connect()
        self.transaction = self.connection.begin()
        self.session = TestingSessionLocal(bind=self.connection)
        self.account = AccountBuilder(self.session).build()
        self.asset = "USDC"
        self.service = LedgerService(self.session, request=self._fake_request())
        self.counter = 0

    def _fake_request(self):
        import uuid
        from types import SimpleNamespace

        return SimpleNamespace(state=SimpleNamespace(request_id=f"req-{uuid.uuid4().hex[:8]}"))

    def teardown(self):
        self.session.close()
        self.transaction.rollback()
        self.connection.close()

    def _balances(self):
        bal = self.service.get_balances(self.account.id).get(
            self.asset, {"available": Decimal("0"), "locked": Decimal("0")}
        )
        return Decimal(bal["available"]), Decimal(bal["locked"])

    @rule(amount=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("200"), places=2))
    def deposit(self, amount):
        self.counter += 1
        self.service.deposit(
            account_id=self.account.id,
            asset=self.asset,
            amount=amount,
            idempotency_key=f"dep-{self.counter}",
            reference_id=f"ref-{self.counter}",
        )
        self.session.commit()

    @rule(amount=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("200"), places=2))
    def lock(self, amount):
        self.counter += 1
        available, _ = self._balances()
        if available < amount:
            return
        self.service.lock_funds(
            payload=schemas.LockIn(
                account_id=self.account.id,
                asset=self.asset,
                amount=amount,
                idempotency_key=f"lock-{self.counter}",
                reference_id=f"ref-{self.counter}",
            )
        )
        self.session.commit()

    @rule(amount=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("200"), places=2))
    def unlock(self, amount):
        self.counter += 1
        _, locked = self._balances()
        if locked < amount:
            return
        self.service.unlock_funds(
            idempotency_key=f"unlock-{self.counter}",
            account_id=self.account.id,
            asset=self.asset,
            amount=amount,
            reference_id=f"ref-{self.counter}",
        )
        self.session.commit()

    @rule(amount=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("200"), places=2))
    def withdraw(self, amount):
        self.counter += 1
        available, _ = self._balances()
        if available < amount:
            return
        self.service.withdraw(
            idempotency_key=f"wd-{self.counter}",
            account_id=self.account.id,
            asset=self.asset,
            amount=amount,
            reference_id=f"ref-{self.counter}",
        )
        self.session.commit()

    #
    @invariant()
    def balances_match_events(self):
        available, locked = self._balances()
        total = available + locked
        # sum deltas for this account/asset
        events_sum = sum(
            Decimal(row[0])
            for row in self.session.execute(
                text(
                    "select e.delta "
                    "from event e "
                    "join assets a on a.id = e.id_asset "
                    "where e.account_id=:account_id and a.nm_asset=:asset "
                    "and e.event_type in ('deposit', 'withdraw')"
                ),
                {"account_id": self.account.id, "asset": self.asset},
            )
        )
        assert available >= 0
        assert locked >= 0
        assert total == events_sum


@pytest.mark.property
def test_state_machine():
    run_state_machine_as_test(
        LedgerStateMachine,
        settings=settings(max_examples=15, stateful_step_count=20, phases=[Phase.generate, Phase.target, Phase.shrink]),
    )
