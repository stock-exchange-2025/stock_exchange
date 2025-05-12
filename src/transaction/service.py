from typing import List

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_session
from src.transaction.schemas import Transaction


async def get_transaction_history(ticker: str, limit: int, db_session: AsyncSession = Depends(get_session)) -> List[Transaction]:
    pass