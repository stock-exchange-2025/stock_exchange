from typing import List

from src.core.schemas import Ok
from src.instrument.schemas import Instrument


async def add_instrument(*, instrument: Instrument) -> Ok:
    pass

async def get_instruments() -> List[Instrument]:
    pass

async def delete_instrument(*, ticker: str) -> Ok:
    pass