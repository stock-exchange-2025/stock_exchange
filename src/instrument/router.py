from typing import Optional, List

from fastapi import APIRouter, Header

from src.core.enums import ApiTags
from src.core.schemas import Ok
from src.instrument import service
from src.instrument.schemas import Instrument

router = APIRouter()


@router.post("/admin/instrument", tags=[ApiTags.ADMIN], response_model=Ok)
async def add_instrument(request: Instrument, authorization: Optional[str] = Header(None)):
    return await service.add_instrument(instrument=request)

@router.get("/public/instrument", tags=[ApiTags.PUBLIC], response_model=List[Instrument])
async def list_instruments():
    return await service.get_instruments()

@router.delete("/admin/instrument/{ticker}", tags=[ApiTags.ADMIN], response_model=Ok)
async def delete_instrument(ticker: str, authorization: Optional[str] = Header(None)):
    return await service.delete_instrument(ticker=ticker)