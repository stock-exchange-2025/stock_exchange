from typing import Optional, List

from fastapi import APIRouter, Header
from pydantic import UUID4

from src.core.schemas import Ok
from src.order import service
from src.order.schemas import CreateOrderResponse, LimitOrderBody, LimitOrder, MarketOrder

router = APIRouter()


@router.post("/order", response_model=CreateOrderResponse)
async def create_order(body: LimitOrderBody, authorization: Optional[str] = Header(None)):
    return await service.create_order(body=body)

@router.get("/order", response_model=List[LimitOrder | MarketOrder])
async def list_orders(authorization: Optional[str] = Header(None)):
    return await service.get_orders()

@router.get("/order/{order_id}", response_model=LimitOrder | MarketOrder)
async def get_order(order_id: UUID4, authorization: Optional[str] = Header(None)):
    return await service.get_order(order_id=order_id)

@router.delete("/order/{order_id}", response_model=Ok)
async def cancel_order(order_id: UUID4, authorization: Optional[str] = Header(None)):
    return await service.cancel_order(order_id=order_id)