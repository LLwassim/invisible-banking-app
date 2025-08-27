from pydantic import BaseModel


class AccountCreate(BaseModel):
    type: str = "checking"


class AccountOut(BaseModel):
    id: int
    type: str
    balance_cents: int
