from typing import List

from fastapi import APIRouter

from src.core.schemas import User, Instrument
from src.public.schemas import NewUser, L2OrderBook, Transaction

router = APIRouter()


@router.post("/register", response_model=User)
async def register(user: NewUser):
    pass

@router.get("/instrument", response_model=List[Instrument])
async def list_instruments():
    pass

@router.get("/orderbook/{ticker}", response_model=L2OrderBook)
async def get_orderbook(ticker: str, limit: int = 0):
    pass

@router.get("/transactions/{ticker}", response_model=List[Transaction])
async def get_transaction_history(ticker: str, limit: int = 0):
    pass