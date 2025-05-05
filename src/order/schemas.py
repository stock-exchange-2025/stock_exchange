from datetime import datetime

from pydantic import BaseModel, UUID4, Field

from src.order.enums import Direction, OrderStatus


class LimitOrderBody(BaseModel):
    direction: Direction
    ticker: str
    qty: float = Field(ge=1)
    price: float = Field(gt=0)


class LimitOrder(BaseModel):
    id: UUID4
    status: OrderStatus
    user_id: UUID4
    timestamp: datetime
    body: LimitOrderBody
    filled: int = 0


class MarketOrderBody(BaseModel):
    direction: Direction
    ticker: str
    qty: int = Field(ge=1)


class MarketOrder(BaseModel):
    id: UUID4
    status: OrderStatus
    user_id: UUID4
    timestamp: datetime
    body: MarketOrderBody


class CreateOrderResponse(BaseModel):
    success: bool = True
    order_id: UUID4