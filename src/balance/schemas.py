from typing import Dict
from uuid import UUID

from pydantic import BaseModel, Field


class BalanceResponse(BaseModel):
    __root__: Dict[str, int]

class BalanceUpdateBody(BaseModel):
    user_id: UUID
    ticker: str = Field(example="MEMECOIN")
    amount: int = Field(gt=0)