from typing import List

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.core.schemas import Ok
from src.dependencies import get_session
from src.instrument.schemas import Instrument


async def add_instrument(*, add_instrument_request: Instrument, request: Request, db_session: AsyncSession = Depends(get_session)) -> Ok:
    pass


async def get_instruments(db_session: AsyncSession = Depends(get_session)) -> List[Instrument]:
    pass


async def delete_instrument(*, ticker: str, request: Request, db_session: AsyncSession = Depends(get_session)) -> Ok:
    pass