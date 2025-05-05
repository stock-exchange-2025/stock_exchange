from typing import Optional

from fastapi import Header, APIRouter
from pydantic import UUID4

from src.admin import service
from src.admin.schemas import BalanceUpdateBody
from src.core.enums import ApiTags
from src.core.schemas import Instrument, User, Ok

router = APIRouter()


@router.post("/instrument", response_model=Ok)
async def add_instrument(request: Instrument, authorization: Optional[str] = Header(None)):
    return await service.add_instrument(instrument=request)

@router.delete("/instrument/{ticker}", response_model=Ok)
async def delete_instrument(ticker: str, authorization: Optional[str] = Header(None)):
    return await service.delete_instrument(ticker=ticker)

@router.post("/balance/deposit", tags=[ApiTags.ADMIN, ApiTags.BALANCE], response_model=Ok)
async def deposit(request: BalanceUpdateBody, authorization: Optional[str] = Header(None)):
    return await service.process_deposit(operation_info=request)

@router.post("/balance/withdraw", tags=[ApiTags.ADMIN, ApiTags.BALANCE], response_model=Ok)
async def withdraw(request: BalanceUpdateBody, authorization: Optional[str] = Header(None)):
    return await service.withdraw(operation_info=request)

@router.delete("/user/{user_id}", tags=[ApiTags.ADMIN, ApiTags.USER], response_model=User)
async def delete_user(user_id: UUID4, authorization: Optional[str] = Header(None)):
    return await service.delete_user(user_id=user_id)