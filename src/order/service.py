from typing import List

from pydantic import UUID4

from src.core.schemas import Ok
from src.order.schemas import LimitOrderBody, CreateOrderResponse, LimitOrder, MarketOrder


async def create_order(*, body: LimitOrderBody) -> CreateOrderResponse:
    pass

async def get_orders() -> List[LimitOrder | MarketOrder]:
    pass

async def get_order(*, order_id: UUID4) -> LimitOrder | MarketOrder:
    pass

async def cancel_order(*, order_id: UUID4) -> Ok:
    pass