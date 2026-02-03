# app/core/log_mapper.py
from typing import Dict
from decimal import Decimal


class LedgerLogMapper:

    @staticmethod
    def deposit(
        *,
        account_id: str,
        asset: str,
        amount: Decimal,
        request_id: str,
        idempotency_key: str
    ) -> Dict:
        return {
            "operation": "deposit",
            "account_id": account_id,
            "asset": asset,
            "amount": str(amount),
            "request_id": request_id,
            "idempotency_key": idempotency_key,
        }

    @staticmethod
    def lock(
        *,
        account_id: str,
        asset: str,
        amount: Decimal,
        request_id: str,
        idempotency_key: str = None,
        reference_id: str = None
    ) -> Dict:
        return {
            "operation": "lock",
            "account_id": account_id,
            "asset": asset,
            "amount": str(amount),
            "request_id": request_id,
            "idempotency_key": idempotency_key,
            "reference_id": reference_id,
        }

    @staticmethod
    def withdraw(
        *,
        account_id: str,
        asset: str,
        amount: Decimal,
        request_id: str,
        idempotency_key: str
    ) -> Dict:
        return {
            "operation": "withdraw",
            "account_id": account_id,
            "asset": asset,
            "amount": str(amount),
            "request_id": request_id,
            "idempotency_key": idempotency_key,
            "success": True,
        }

    class Config:
        extra = "ignore"