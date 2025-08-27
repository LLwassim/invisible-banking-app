from typing import Optional
from sqlmodel import SQLModel, Field


class Account(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    type: str = Field(default="checking")
    balance_cents: int = Field(default=0)
