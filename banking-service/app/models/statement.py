from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Statement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="account.id")
    period_start: datetime = Field()
    period_end: datetime = Field()
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    opening_balance_cents: int = Field()
    closing_balance_cents: int = Field()
