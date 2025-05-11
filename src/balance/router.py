from typing import Optional
from fastapi import APIRouter, Header, Depends
from starlette.requests import Request

from src.balance import service
from src.balance.schemas import BalanceResponse, BalanceUpdateBody
from src.core.database import DbSession, get_db
from src.core.enums import ApiTags
from src.core.schemas import Ok

router = APIRouter()


@router.get("/balance", tags=[ApiTags.BALANCE], response_model=BalanceResponse)
def get_balances(request: Request = None, db_session: DbSession = Depends(get_db)):
    return service.get_balances()


@router.post("/admin/balance/deposit", tags=[ApiTags.ADMIN, ApiTags.BALANCE], response_model=Ok)
def deposit(balance_update_request: BalanceUpdateBody, request: Request = None, db_session: DbSession = Depends(get_db)):
    return service.process_deposit(operation_info=balance_update_request)


@router.post("/admin/balance/withdraw", tags=[ApiTags.ADMIN, ApiTags.BALANCE], response_model=Ok)
def withdraw(balance_update_request: BalanceUpdateBody, request: Request = None, db_session: DbSession = Depends(get_db)):
    return service.withdraw(operation_info=balance_update_request)