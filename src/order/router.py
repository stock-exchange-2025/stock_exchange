from typing import Optional, List

from fastapi import APIRouter, Header
from pydantic import UUID4

from src.core.enums import ApiTags
from src.core.schemas import Ok
from src.order import service
from src.order.schemas import CreateOrderResponse, LimitOrderBody, LimitOrder, MarketOrder, L2OrderBook

router = APIRouter()


@router.post("/order", tags=[ApiTags.ORDER], response_model=CreateOrderResponse)
async def create_order(body: LimitOrderBody, authorization: Optional[str] = Header(None)):
    return await service.create_order(body=body)

@router.get("/order", tags=[ApiTags.ORDER], response_model=List[LimitOrder | MarketOrder])
async def list_orders(authorization: Optional[str] = Header(None)):
    return await service.get_orders()

@router.get("/public/orderbook/{ticker}", tags=[ApiTags.PUBLIC], response_model=L2OrderBook)
async def get_orderbook(ticker: str, limit: int = 0):
    return await service.get_orderbook(ticker=ticker, limit=limit)

@router.get("/order/{order_id}", tags=[ApiTags.ORDER], response_model=LimitOrder | MarketOrder)
async def get_order(order_id: UUID4, authorization: Optional[str] = Header(None)):
    return await service.get_order(order_id=order_id)

@router.delete("/order/{order_id}", tags=[ApiTags.ORDER], response_model=Ok)
async def cancel_order(order_id: UUID4, authorization: Optional[str] = Header(None)):
    return await service.cancel_order(order_id=order_id)