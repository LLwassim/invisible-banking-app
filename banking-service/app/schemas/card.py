from pydantic import BaseModel


class CardIssueRequest(BaseModel):
    account_id: int
    holder_name: str
    exp_month: int
    exp_year: int
    cvv: str


class CardOut(BaseModel):
    id: int
    brand: str
    holder_name: str
    last4: str
    card_token: str
    exp_month: int
    exp_year: int
