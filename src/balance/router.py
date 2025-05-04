from typing import Optional
from fastapi import APIRouter, Header

from src.balance.schemas import BalanceResponse

router = APIRouter()


@router.get("/balance", response_model=BalanceResponse)
async def get_balances(authorization: Optional[str] = Header(None)):
    pass