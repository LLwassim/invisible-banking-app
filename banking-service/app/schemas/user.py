from typing import Optional
from pydantic import BaseModel


class UserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
