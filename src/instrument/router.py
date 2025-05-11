from typing import Optional, List

from fastapi import APIRouter, Header, Depends
from starlette.requests import Request

from src.core.database import DbSession, get_db
from src.core.enums import ApiTags
from src.core.schemas import Ok
from src.instrument import service
from src.instrument.schemas import Instrument

router = APIRouter()


@router.post("/admin/instrument", tags=[ApiTags.ADMIN], response_model=Ok)
def add_instrument(add_instrument_request: Instrument, request: Request = None, db_session: DbSession = Depends(get_db)):
    return service.add_instrument(add_instrument_request=add_instrument_request, request=request, db_session=db_session)


@router.get("/public/instrument", tags=[ApiTags.PUBLIC], response_model=List[Instrument])
def list_instruments(db_session: DbSession = Depends(get_db)):
    return service.get_instruments(db_session=db_session)


@router.delete("/admin/instrument/{ticker}", tags=[ApiTags.ADMIN], response_model=Ok)
def delete_instrument(ticker: str, request: Request = None, db_session: DbSession = Depends(get_db)):
    return service.delete_instrument(ticker=ticker, request=request, db_session=db_session)