from typing import List

from pydantic import UUID4
from starlette.requests import Request

from src.core.database import DbSession
from src.core.schemas import Ok
from src.order.schemas import LimitOrderBody, CreateOrderResponse, LimitOrder, MarketOrder, L2OrderBook


def create_order(*, body: LimitOrderBody, request: Request, db_session: DbSession) -> CreateOrderResponse:
    pass


def get_orders(*, request: Request, db_session: DbSession) -> List[LimitOrder | MarketOrder]:
    pass


def get_order(*, order_id: UUID4, request: Request, db_session: DbSession) -> LimitOrder | MarketOrder:
    pass


def get_orderbook(*, ticker: str, limit: int, db_session: DbSession) -> L2OrderBook:
    pass


def cancel_order(*, order_id: UUID4, request: Request, db_session: DbSession) -> Ok:
    pass