from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST

from src.dependencies import get_session
from src.transaction.models import Transaction as TransactionDAL
from src.instrument.models import Instrument as InstrumentDAL


async def get_transaction_history(ticker: str, limit: int, db_session: AsyncSession = Depends(get_session)) -> List[TransactionDAL]:
    async with db_session.begin():
        existing_instrument = (
            await db_session.scalar(
                select(InstrumentDAL)
                .where(InstrumentDAL.ticker == ticker))
        )

        if existing_instrument is None:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=[{
                    "loc": ["body", "name"],
                    "msg": f"Instrument with ticker '{ticker}' doesn't exists.",
                    "type": "value_error"
                }]
            )

        result = await db_session.execute(
            select(TransactionDAL)
            .where(TransactionDAL.instrument_id == existing_instrument.id)
            .order_by(TransactionDAL.timestamp.desc())
            .limit(limit)
        )

        transactions = result.scalars().all()

        return [
            TransactionDAL(
                ticker=ticker,
                amount=tx.amount,
                price=tx.price,
                timestamp=tx.timestamp
            )
            for tx in transactions
        ]