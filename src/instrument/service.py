import uuid

from fastapi import HTTPException
from typing import List

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.status import HTTP_409_CONFLICT

from src.core.schemas import Ok
from src.dependencies import get_session
from src.instrument.schemas import Instrument as InstrumentDTO
from src.instrument.models import Instrument as InstrumentDAL


async def create_instrument(*, add_instrument_request: InstrumentDTO, db_session: AsyncSession = Depends(get_session)) -> Ok:
    existing_instrument = (await db_session.execute(
        select(InstrumentDAL).where(InstrumentDAL.ticker == add_instrument_request.ticker)
    )).scalar_one_or_none()

    if existing_instrument:
        raise HTTPException(status_code=HTTP_409_CONFLICT, detail="Instrument with same ticker already exists.")

    new_instrument = InstrumentDAL(
        id=uuid.uuid4(),
        name=add_instrument_request.name,
        ticker=add_instrument_request.ticker
    )

    db_session.add(new_instrument)
    await db_session.commit()

    return Ok()


async def get_instruments(db_session: AsyncSession = Depends(get_session)) -> List[InstrumentDTO]:
    pass


async def delete_instrument(*, ticker: str, request: Request, db_session: AsyncSession = Depends(get_session)) -> Ok:
    pass