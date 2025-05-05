from pydantic import UUID4

from src.admin.schemas import BalanceUpdateBody
from src.core.schemas import Instrument, Ok, User


async def add_instrument(*, instrument: Instrument) -> Ok:
    pass

async def delete_instrument(*, ticker: str) -> Ok:
    pass

async def process_deposit(*, operation_info: BalanceUpdateBody) -> Ok:
    pass

async def withdraw(*, operation_info: BalanceUpdateBody) -> Ok:
    pass

async def delete_user(*, user_id: UUID4) -> User:
    pass