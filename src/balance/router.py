from typing import Optional
from fastapi import APIRouter, Header

from src.balance import service
from src.balance.schemas import BalanceResponse, BalanceUpdateBody
from src.core.enums import ApiTags
from src.core.schemas import Ok

router = APIRouter()


@router.get("/balance", tags=[ApiTags.BALANCE], response_model=BalanceResponse)
async def get_balances(authorization: Optional[str] = Header(None)):
    return await service.get_balances()

@router.post("/admin/balance/deposit", tags=[ApiTags.ADMIN, ApiTags.BALANCE], response_model=Ok)
async def deposit(request: BalanceUpdateBody, authorization: Optional[str] = Header(None)):
    return await service.process_deposit(operation_info=request)

@router.post("/admin/balance/withdraw", tags=[ApiTags.ADMIN, ApiTags.BALANCE], response_model=Ok)
async def withdraw(request: BalanceUpdateBody, authorization: Optional[str] = Header(None)):
    return await service.withdraw(operation_info=request)