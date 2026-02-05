from typing import Dict


class LedgerErrorLogMapper:
    @staticmethod
    def insufficient_funds(
        *,
        account_id: str,
        asset: str,
        amount: str,
        request_id: str,
        idempotency_key: str,
        reference_id: str = None,
    ) -> Dict:
        return {
            "error_type": "INSUFFICIENT_FUNDS",
            "error_code": "LEDGER_001",
            "impact": "none",
            "account_id": account_id,
            "asset": asset,
            "amount": amount,
            "request_id": request_id,
            "idempotency_key": idempotency_key,
            "reference_id": reference_id,
        }

    @staticmethod
    def negative_amount(
        *,
        account_id: str,
        asset: str,
        amount: str,
        request_id: str,
        idempotency_key: str,
    ) -> Dict:
        return {
            "operation": "withdraw",
            "error_type": "NEGATIVE_AMOUNT",
            "error_code": "LEDGER_002",
            "impact": "none",
            "account_id": account_id,
            "asset": asset,
            "amount": amount,
            "request_id": request_id,
            "idempotency_key": idempotency_key,
        }

    @staticmethod
    def invalid_asset(
        *,
        account_id: str,
        asset: str,
        amount: str,
        request_id: str,
        idempotency_key: str,
    ) -> Dict:
        return {
            "operation": "withdraw",
            "error_type": "INVALID_ASSET",
            "error_code": "LEDGER_003",
            "impact": "none",
            "account_id": account_id,
            "asset": asset,
            "amount": amount,
            "request_id": request_id,
            "idempotency_key": idempotency_key,
        }

    @staticmethod
    def balance_not_found(
        *,
        account_id: str,
        asset: str,
        request_id: str,
        idempotency_key: str,
    ) -> Dict:
        return {
            "operation": "withdraw",
            "error_type": "BALANCE_NOT_FOUND",
            "error_code": "LEDGER_004",
            "impact": "none",
            "account_id": account_id,
            "asset": asset,
            "request_id": request_id,
            "idempotency_key": idempotency_key,
        }

    @staticmethod
    def invalid_operation(
        *,
        account_id: str,
        asset: str,
        amount: str,
        request_id: str,
        idempotency_key: str,
        operation="withdraw",
    ) -> Dict:
        return {
            "operation": operation,
            "error_type": "INVALID_OPERATION",
            "error_code": "LEDGER_005",
            "impact": "none",
            "account_id": account_id,
            "asset": asset,
            "amount": amount,
            "request_id": request_id,
            "idempotency_key": idempotency_key,
        }

    @staticmethod
    def lock_exceeds_available(
        *,
        account_id: str,
        asset: str,
        amount: str,
        request_id: str,
        idempotency_key: str,
        reference_id: str = None,
    ) -> Dict:
        return {
            "operation": "lock",
            "error_type": "LOCK_EXCEEDS_AVAILABLE",
            "error_code": "LEDGER_006",
            "impact": "none",
            "account_id": account_id,
            "asset": asset,
            "amount": amount,
            "request_id": request_id,
            "idempotency_key": idempotency_key,
            "reference_id": reference_id,
        }

    @staticmethod
    def unlock_exceeds_locked(
        *,
        account_id: str,
        asset: str,
        amount: str,
        request_id: str,
        idempotency_key: str,
    ) -> Dict:
        return {
            "operation": "unlock",
            "error_type": "UNLOCK_EXCEEDS_LOCKED",
            "error_code": "LEDGER_007",
            "impact": "none",
            "account_id": account_id,
            "asset": asset,
            "amount": amount,
            "request_id": request_id,
            "idempotency_key": idempotency_key,
        }

    @staticmethod
    def settle_exceeds_locked(
        *,
        account_id: str,
        asset: str,
        amount: str,
        request_id: str,
        idempotency_key: str,
    ) -> Dict:
        return {
            "operation": "settle",
            "error_type": "SETTLE_EXCEEDS_LOCKED",
            "error_code": "LEDGER_008",
            "impact": "none",
            "account_id": account_id,
            "asset": asset,
            "amount": amount,
            "request_id": request_id,
            "idempotency_key": idempotency_key,
        }

    @staticmethod
    def event_exists(
        *,
        account_id: str,
        asset: str,
        amount: str,
        request_id: str,
        idempotency_key: str,
        reference_id: str = None,
        operation="create_event",
    ) -> Dict:
        return {
            "operation": operation,
            "error_type": "EVENT_EXISTS",
            "error_code": "LEDGER_009",
            "impact": "none",
            "account_id": account_id,
            "asset": asset,
            "amount": amount,
            "request_id": request_id,
            "idempotency_key": idempotency_key,
            "reference_id": reference_id,
        }
