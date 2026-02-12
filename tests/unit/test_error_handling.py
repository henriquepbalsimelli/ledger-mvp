import uuid
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app import main as main_module
from app.core.exceptions import InsufficientFunds
from app.core.ledger_logger import LedgerErrorLogger
from app.ledger.services.ledger import LedgerService
from tests.builders.account_builder import AccountBuilder
from tests.conftest import TestingSessionLocal


def test_global_exception_handler_logs_once(monkeypatch):
    # add a temporary route that raises
    app = main_module.app
    original_routes = list(app.router.routes)
    app.router.routes = [r for r in app.router.routes if getattr(r, "path", None) != "/boom"]

    @app.get("/boom")
    def boom():
        raise RuntimeError("boom")

    mock_logger = MagicMock()
    monkeypatch.setattr(main_module, "logger", mock_logger)

    # prevent TestClient from re-raising server exceptions so global handler runs
    with TestClient(app, raise_server_exceptions=False) as client:
        resp = client.get("/boom", headers={"X-Request-Id": "test-req"})

    assert resp.status_code == 500
    mock_logger.exception.assert_called_once()
    app.router.routes = original_routes


def test_custom_exception_logger_called(monkeypatch, request_mock):
    session = TestingSessionLocal()
    account = AccountBuilder(session, guid=uuid.uuid4()).build()
    service = LedgerService(session, request_mock)
    service.deposit(
        account_id=account.id,
        asset="USDC",
        amount=Decimal("10"),
        idempotency_key="dep-log",
        reference_id="ref",
    )

    called = {}

    def fake_insufficient_funds(self, **payload):
        called["insufficient"] = payload

    monkeypatch.setattr(LedgerErrorLogger, "insufficient_funds", fake_insufficient_funds)

    with pytest.raises(InsufficientFunds):
        service.withdraw(
            account_id=account.id,
            asset="USDC",
            amount=Decimal("100"),
            idempotency_key="wd-log",
            reference_id="ref2",
        )

    assert "insufficient" in called
    session.close()
