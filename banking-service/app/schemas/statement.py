from datetime import datetime
from pydantic import BaseModel


class StatementRequest(BaseModel):
    month: str  # Format: "YYYY-MM"


class StatementOut(BaseModel):
    id: int
    account_id: int
    period_start: datetime
    period_end: datetime
    opening_balance_cents: int
    closing_balance_cents: int
