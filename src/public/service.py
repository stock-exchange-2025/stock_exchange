from typing import List

from src.core.schemas import User, Instrument
from src.public.schemas import NewUser, L2OrderBook, Transaction


async def register_new_user(*, user: NewUser) -> User:
    pass

async def get_instruments() -> List[Instrument]:
    pass

async def get_orderbook(*, ticker: str, limit: int = 0) -> L2OrderBook:
    pass

async def get_transaction_history(ticker: str, limit: int = 0) -> List[Transaction]:
    pass