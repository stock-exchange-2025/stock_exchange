from typing import List

from src.core.database import DbSession
from src.transaction.schemas import Transaction


def get_transaction_history(ticker: str, limit: int, db_session: DbSession) -> List[Transaction]:
    pass