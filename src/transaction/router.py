from typing import List

from fastapi import APIRouter

from src.core.enums import ApiTags
from src.transaction import service
from src.transaction.schemas import Transaction

router = APIRouter()


@router.get("/public/transactions/{ticker}", tags=[ApiTags.PUBLIC], response_model=List[Transaction])
async def get_transaction_history(ticker: str, limit: int = 0):
    return await service.get_transaction_history(ticker=ticker, limit=limit)