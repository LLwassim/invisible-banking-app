from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DepositWithdrawRequest(BaseModel):
    amount_cents: int
    description: Optional[str] = None


class TransactionOut(BaseModel):
    id: int
    type: str
    amount_cents: int
    created_at: datetime
    description: Optional[str] = None


class TransferRequest(BaseModel):
    from_account_id: int
    to_account_id: int
    amount_cents: int
    description: Optional[str] = None
