from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="account.id")
    type: str = Field()  # deposit, withdraw, transfer_in, transfer_out, card_charge, card_refund
    amount_cents: int = Field()
    created_at: datetime = Field(default_factory=datetime.utcnow)
    description: Optional[str] = None
    counterparty_account_id: Optional[int] = None
