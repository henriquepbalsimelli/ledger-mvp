from decimal import Decimal
from typing import Dict, Optional

from pydantic import BaseModel


class BalanceOut(BaseModel):
    available: Optional[Decimal]
    locked: Optional[Decimal]


class BalancesResponse(BaseModel):
    account_id: str
    balances: Optional[Dict[str, BalanceOut]] = None
