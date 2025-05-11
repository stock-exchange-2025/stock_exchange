from typing import List

from starlette.requests import Request

from src.core.database import DbSession
from src.core.schemas import Ok
from src.instrument.schemas import Instrument


def add_instrument(*, add_instrument_request: Instrument, request: Request, db_session: DbSession) -> Ok:
    pass


def get_instruments(*, db_session: DbSession) -> List[Instrument]:
    pass


def delete_instrument(*, ticker: str, request: Request, db_session: DbSession) -> Ok:
    pass