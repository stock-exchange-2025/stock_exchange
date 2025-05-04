from typing import Optional, List

from fastapi import APIRouter, Header

from src.core.schemas import Ok
from src.order.schemas import CreateOrderResponse, LimitOrderBody, LimitOrder

router = APIRouter()


@router.post("/order", response_model=CreateOrderResponse)
async def create_order(body: LimitOrderBody, authorization: Optional[str] = Header(None)):
    pass

@router.get("/order", response_model=List[LimitOrder])
async def list_orders(authorization: Optional[str] = Header(None)):
    pass

@router.get("/order/{order_id}", response_model=LimitOrder)
async def get_order(order_id: str, authorization: Optional[str] = Header(None)):
    pass

@router.delete("/order/{order_id}", response_model=Ok)
async def cancel_order(order_id: str, authorization: Optional[str] = Header(None)):
    pass