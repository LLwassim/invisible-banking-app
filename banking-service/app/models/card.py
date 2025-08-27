from typing import Optional
from sqlmodel import SQLModel, Field


class Card(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="account.id")
    brand: str = Field(default="VISA")
    holder_name: str = Field()
    last4: str = Field()
    card_token: str = Field()
    exp_month: int = Field()
    exp_year: int = Field()
    cvv_hash: str = Field()
