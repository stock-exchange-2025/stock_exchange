from typing import List

from fastapi import Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.core.schemas import Ok
from src.dependencies import get_session
from src.order.schemas import LimitOrderBody, CreateOrderResponse, LimitOrder, MarketOrder, L2OrderBook


async def create_order(*, body: LimitOrderBody, request: Request, db_session: AsyncSession = Depends(get_session)) -> CreateOrderResponse:
    pass


async def get_orders(*, request: Request, db_session: AsyncSession = Depends(get_session)) -> List[LimitOrder | MarketOrder]:
    pass


async def get_order(*, order_id: UUID4, request: Request, db_session: AsyncSession = Depends(get_session)) -> LimitOrder | MarketOrder:
    pass


async def get_orderbook(*, ticker: str, limit: int, db_session: AsyncSession = Depends(get_session)) -> L2OrderBook:
    pass


async def cancel_order(*, order_id: UUID4, request: Request, db_session: AsyncSession = Depends(get_session)) -> Ok:
    pass