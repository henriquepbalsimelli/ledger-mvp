# app/core/ledger_logger.py
import logging

from starlette.requests import Request

from app.core.error_log_mapper import LedgerErrorLogMapper
from app.core.log_mapper import LedgerLogMapper
from app.core.logger import ContextLogger


class LedgerLogger:
    def __init__(self, logger_name: str, request: Request):
        self._logger = logging.getLogger(logger_name)
        self.request = request

    def deposit(self, **kwargs):
        data = LedgerLogMapper.deposit(**kwargs, request_id=self.request.state.request_id)
        ContextLogger(self._logger, data).info("deposit")

    def lock(self, **kwargs):
        data = LedgerLogMapper.lock(**kwargs, request_id=self.request.state.request_id)
        ContextLogger(self._logger, data).info("lock")

    def withdraw(self, **kwargs):
        data = LedgerLogMapper.withdraw(**kwargs, request_id=self.request.state.request_id)
        ContextLogger(self._logger, data).info("withdraw")


class LedgerErrorLogger:
    def __init__(self, logger_name: str, request: Request):
        self._logger = logging.getLogger(logger_name)
        self.request = request

    def insufficient_funds(self, **kwargs):
        data = LedgerErrorLogMapper.insufficient_funds(**kwargs, request_id=self.request.state.request_id)
        ContextLogger(self._logger, data).warning("insufficient_funds")

    def negative_amount(self, **kwargs):
        data = LedgerErrorLogMapper.negative_amount(**kwargs, request_id=self.request.state.request_id)
        ContextLogger(self._logger, data).warning("negative_amount")

    def invalid_asset(self, **kwargs):
        data = LedgerErrorLogMapper.invalid_asset(**kwargs, request_id=self.request.state.request_id)
        ContextLogger(self._logger, data).warning("invalid_asset")

    def balance_not_found(self, **kwargs):
        data = LedgerErrorLogMapper.balance_not_found(**kwargs, request_id=self.request.state.request_id)
        ContextLogger(self._logger, data).warning("balance_not_found")

    def invalid_operation(self, **kwargs):
        data = LedgerErrorLogMapper.invalid_operation(**kwargs, request_id=self.request.state.request_id)
        ContextLogger(self._logger, data).warning("invalid_operation")

    def lock_exceeds_available(self, **kwargs):
        data = LedgerErrorLogMapper.lock_exceeds_available(**kwargs, request_id=self.request.state.request_id)
        ContextLogger(self._logger, data).warning("lock_exceeds_available")

    def unlock_exceeds_locked(self, **kwargs):
        data = LedgerErrorLogMapper.unlock_exceeds_locked(**kwargs, request_id=self.request.state.request_id)
        ContextLogger(self._logger, data).warning("unlock_exceeds_locked")

    def settle_exceeds_locked(self, **kwargs):
        data = LedgerErrorLogMapper.settle_exceeds_locked(**kwargs, request_id=self.request.state.request_id)
        ContextLogger(self._logger, data).warning("settle_exceeds_locked")

    def event_exists(self, **kwargs):
        data = LedgerErrorLogMapper.event_exists(**kwargs, request_id=self.request.state.request_id)
        ContextLogger(self._logger, data).warning("event_exists")

    def invalid_settlement_state(self, **kwargs):
        data = LedgerErrorLogMapper.invalid_settlement_state(**kwargs, request_id=self.request.state.request_id)
        ContextLogger(self._logger, data).warning("invalid_settlement_state")
