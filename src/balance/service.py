import uuid
from typing import Dict

from fastapi import Depends
from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.status import HTTP_400_BAD_REQUEST

from src.balance.models import Balance
from src.balance.schemas import BalanceResponse, BalanceUpdateBody
from src.core.schemas import Ok
from src.dependencies import get_session
from src.instrument.models import Instrument
from src.user.enums import UserRole


async def get_balances(*, request: Request, db_session: AsyncSession = Depends(get_session)) -> BalanceResponse:
    balance_query = (
        select(Instrument.ticker, Balance.amount)
        .join(Balance, Balance.instrument_id == Instrument.id)
        .where(Balance.user_id == request.state.user.id)
    )

    query_result = await db_session.execute(balance_query)

    balances = query_result.all()

    user_balances: Dict[str, int] = {
        ticker: amount for ticker, amount in balances
    }
    return BalanceResponse.model_validate(user_balances)


async def create_deposit(*, operation_info: BalanceUpdateBody, request: Request, db_session: AsyncSession = Depends(get_session)) -> Ok:
    user = request.state.user

    if user.role != UserRole.admin:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Only admin can make deposit.")

    async with db_session.begin():
        try:
            instrument_id = (
                await db_session.execute(
                    select(Instrument.id)
                    .where(
                        Instrument.ticker == operation_info.ticker,
                        Instrument.is_active == True
                    )
                )
            ).scalar_one()
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Instrument with ticker {operation_info.ticker} not found"
            )

        await db_session.execute(
            insert(Balance)
            .values(
                user_id=operation_info.user_id,
                instrument_id=instrument_id,
                amount=operation_info.amount
            )
            .on_conflict_do_update(
                index_elements=['user_id', 'instrument_id'],
                set_={'amount': Balance.amount + operation_info.amount}
            )
        )

    return Ok(success=True)


async def create_withdraw(*, operation_info: BalanceUpdateBody, request: Request, db_session: AsyncSession = Depends(get_session)) -> Ok:
    user = request.state.user

    if user.role != UserRole.admin:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Only admin can make withdraw.")

    async with db_session.begin():
        result = await db_session.execute(
            select(Instrument.id, Balance.amount)
            .join(Balance, Balance.instrument_id == Instrument.id)
            .where(
                Instrument.ticker == operation_info.ticker,
                Balance.user_id == operation_info.user_id
            )
            .with_for_update()
        )

        instrument_id, current_balance_amount = result.scalar_one()

        if current_balance_amount < operation_info.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient funds"
            )

        await db_session.execute(
            update(Balance)
            .where(
                Balance.user_id == operation_info.user_id,
                Balance.instrument_id == instrument_id
            )
            .values(amount=Balance.amount - operation_info.amount)
        )

    return Ok(success=True)