from typing import List

from pydantic import BaseModel


class NewUser(BaseModel):
    name: str


class OrderBookLevel(BaseModel):
    price: int
    qty: int


class L2OrderBook(BaseModel):
    bid_levels: List[OrderBookLevel]
    ask_levels: List[OrderBookLevel]


class Transaction(BaseModel):
    ticker: str
    amount: int
    price: int
    timestamp: str