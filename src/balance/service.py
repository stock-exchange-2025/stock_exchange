from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.balance.schemas import BalanceResponse, BalanceUpdateBody
from src.core.schemas import Ok
from src.dependencies import get_session


async def get_balances(*, request: Request, db_session: AsyncSession = Depends(get_session)) -> BalanceResponse:
    pass


async def create_deposit(*, operation_info: BalanceUpdateBody, request: Request, db_session: AsyncSession = Depends(get_session)) -> Ok:
    pass


async def create_withdraw(*, operation_info: BalanceUpdateBody, request: Request, db_session: AsyncSession = Depends(get_session)) -> Ok:
    pass