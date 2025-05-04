from enum import Enum

from pydantic import BaseModel

from src.order.enums import OrderDirection, OrderStatus


class LimitOrderBody(BaseModel):
    direction: OrderDirection
    ticker: str
    qty: float
    price: float


class LimitOrder(BaseModel):
    id: str
    status: OrderStatus
    user_id: str
    timestamp: str
    body: LimitOrderBody
    filled: int


class CreateOrderResponse(BaseModel):
    success: bool = True
    order_id: str