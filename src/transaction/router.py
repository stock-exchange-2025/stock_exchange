from typing import List

from fastapi import APIRouter, Depends

from src.core.database import DbSession, get_db
from src.core.enums import ApiTags
from src.transaction import service
from src.transaction.schemas import Transaction

router = APIRouter()


@router.get("/public/transactions/{ticker}", tags=[ApiTags.PUBLIC], response_model=List[Transaction])
def get_transaction_history(ticker: str, limit: int = 0, db_session: DbSession = Depends(get_db)):
    return service.get_transaction_history(ticker=ticker, limit=limit, db_session=db_session)