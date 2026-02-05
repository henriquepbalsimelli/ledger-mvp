# app/ledger/router.py
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.core.db import get_db
from app.ledger import schemas
from app.ledger.services.ledger import InsufficientFunds, LedgerService

router = APIRouter(prefix="/ledger", tags=["ledger"])


@router.get("/balances", response_model=schemas.BalancesResponse)
def get_balances(account_id: str, request: Request, db: Session = Depends(get_db)):
    service = LedgerService(db, request=request)
    balances = service.get_balances(account_id)
    return schemas.BalancesResponse(account_id=account_id, balances=balances)


@router.post("/lock")
def lock(payload: schemas.LockIn, request: Request, db: Session = Depends(get_db)):
    try:
        service = LedgerService(db, request)
        _, bal = service.lock_funds(payload=payload, request=request)
        return schemas.BalancesResponse(
            account_id=payload.account_id,
            balances={payload.asset: schemas.BalanceOut(available=Decimal(bal.available), locked=Decimal(bal.locked))},
        )
    except InsufficientFunds as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/unlock")
def unlock(payload: schemas.Unlock, request: Request, db: Session = Depends(get_db)):
    try:
        service = LedgerService(db, request)
        _, bal = service.unlock_funds(
            idempotency_key=payload.idempotency_key,
            account_id=payload.account_id,
            asset=payload.asset,
            amount=payload.amount,
            reference_id=payload.reference_id,
        )
        return schemas.BalancesResponse(
            account_id=payload.account_id,
            balances={payload.asset: schemas.BalanceOut(available=Decimal(bal.available), locked=Decimal(bal.locked))},
        )
    except InsufficientFunds as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/deposit")
def deposit(payload: schemas.DepositRequest, request: Request, db: Session = Depends(get_db)):
    service = LedgerService(db, request)
    _, bal = service.deposit(
        idempotency_key=payload.idempotency_key,
        account_id=payload.account_id,
        asset=payload.asset,
        amount=payload.amount,
        reference_id=payload.reference_id,
    )
    return schemas.BalancesResponse(
        account_id=payload.account_id,
        balances={payload.asset: schemas.BalanceOut(available=Decimal(bal.available), locked=Decimal(bal.locked))},
    )


@router.post("/withdraw")
def withdraw(payload: schemas.WithdrawRequest, request: Request, db: Session = Depends(get_db)):
    try:
        service = LedgerService(db, request)
        _, bal = service.withdraw(
            idempotency_key=payload.idempotency_key,
            account_id=payload.account_id,
            asset=payload.asset,
            amount=payload.amount,
            reference_id=payload.reference_id,
        )
        return schemas.BalancesResponse(
            account_id=payload.account_id,
            balances={payload.asset: schemas.BalanceOut(available=Decimal(bal.available), locked=Decimal(bal.locked))},
        )
    except InsufficientFunds as e:
        raise HTTPException(status_code=409, detail=str(e))
