from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class NewUser(BaseModel):
    name: str = Field(min_length=3)


class Level(BaseModel):
    price: int
    qty: int


class L2OrderBook(BaseModel):
    bid_levels: List[Level]
    ask_levels: List[Level]


class Transaction(BaseModel):
    ticker: str
    amount: int
    price: int
    timestamp: datetime