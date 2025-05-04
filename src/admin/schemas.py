from pydantic import BaseModel

from src.core.enums import Ticker


class BalanceUpdateBody(BaseModel):
    user_id: str
    ticker: Ticker
    amount: int