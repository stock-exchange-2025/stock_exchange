from starlette.requests import Request

from src.balance.schemas import BalanceResponse, BalanceUpdateBody
from src.core.database import DbSession
from src.core.schemas import Ok


def get_balances(*, request: Request, db_session: DbSession) -> BalanceResponse:
    pass


def process_deposit(*, operation_info: BalanceUpdateBody, request: Request, db_session: DbSession) -> Ok:
    pass


def withdraw(*, operation_info: BalanceUpdateBody, request: Request, db_session: DbSession) -> Ok:
    pass