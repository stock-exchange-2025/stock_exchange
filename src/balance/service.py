from src.balance.schemas import BalanceResponse, BalanceUpdateBody
from src.core.schemas import Ok


async def get_balances() -> BalanceResponse:
    pass

async def process_deposit(*, operation_info: BalanceUpdateBody) -> Ok:
    pass

async def withdraw(*, operation_info: BalanceUpdateBody) -> Ok:
    pass