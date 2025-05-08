from typing import List

from src.transaction.schemas import Transaction


async def get_transaction_history(ticker: str, limit: int = 0) -> List[Transaction]:
    pass