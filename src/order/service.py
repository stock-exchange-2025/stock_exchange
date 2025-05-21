from datetime import datetime
from decimal import Decimal
from typing import List

from fastapi import Depends, HTTPException
from pydantic import UUID4
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.balance import Balance
from src.core.schemas import Ok
from src.dependencies import get_session
from src.instrument import Instrument
from src.order import Order
from src.order.constants import DEFAULT_TICKER
from src.order.enums import OrderStatus, Direction, OrderType
from src.order.schemas import LimitOrderBody, CreateOrderResponse, LimitOrder, MarketOrder, L2OrderBook, Level, \
    MarketOrderBody
from src.transaction import Transaction


async def create_order(*, body: LimitOrderBody, request: Request, db_session: AsyncSession = Depends(get_session)) -> CreateOrderResponse:
    user = request.state.user

    async with db_session.begin():
        instrument = await db_session.scalar(
            select(Instrument).where(Instrument.ticker == body.ticker and Instrument.is_active == True)
        )

        if instrument is None:
            raise HTTPException(status_code=404, detail="Ticker not found or delisted")

        quote_instrument = await db_session.scalar(
            select(Instrument).where(Instrument.ticker == DEFAULT_TICKER)
        )

        if quote_instrument is None:
            raise HTTPException(status_code=500, detail="RUB instrument not found")

        balances = {
            "instrument": await db_session.scalar(
                select(Balance).where(Balance.user_id == user.id, Balance.instrument_id == instrument.id)
            ),
            "quote": await db_session.scalar(
                select(Balance).where(Balance.user_id == user.id, Balance.instrument_id == quote_instrument.id)
            )
        }

        for balance_type, balance in balances.items():
            if balance is None:
                balance = Balance(
                    user_id=user.id,
                    instrument_id=instrument.id if balance_type == "instrument" else quote_instrument.id,
                    amount=0,
                    locked_amount=0
                )
                balances[balance_type] = balance
                db_session.add(balance)

        qty = body.qty

        price = body.price if isinstance(body, LimitOrderBody) else 0

        required = qty * price if body.direction == Direction.buy and isinstance(body, LimitOrderBody) else qty
        available = balances["quote"].amount - balances["quote"].locked_amount if body.direction == Direction.buy else \
            balances["instrument"].amount - balances["instrument"].locked_amount
        if available < required:
            raise HTTPException(status_code=400,
                                detail=f"Insufficient {'funds' if body.direction == Direction.buy else 'stock'}")

        if body.direction == Direction.buy and isinstance(body, LimitOrderBody):
            balances["quote"].locked_amount += Decimal(str(required))
        else:
            balances["instrument"].locked_amount += qty

        if isinstance(body, MarketOrderBody):
            matching_order = await db_session.scalar(
                select(Order)
                .where(
                    Order.instrument_id == instrument.id,
                    Order.direction == (Direction.sell if body.direction == Direction.buy else Direction.buy),
                    Order.status == OrderStatus.new
                )
                .order_by(Order.price.asc() if body.direction == Direction.buy else Order.price.desc(),
                          Order.created_at.asc()).limit(1)
            )
            if matching_order is None:
                raise HTTPException(status_code=400, detail="No matching order available")

            trade_price = matching_order.price
            trade_qty = min(qty, matching_order.quantity - matching_order.filled_quantity)

            matching_order.filled_quantity += trade_qty
            matching_order.status = OrderStatus.executed if matching_order.filled_quantity == matching_order.quantity else \
                OrderStatus.partially_filled

            if body.direction == Direction.buy:
                balances["quote"].locked_amount -= trade_qty * trade_price
                balances["instrument"].amount += trade_qty
            else:
                balances["instrument"].locked_amount -= trade_qty
                balances["quote"].amount += trade_qty * trade_price

            transaction = Transaction(
                order_id=matching_order.id,
                instrument_id=instrument.id,
                price=trade_price,
                quantity=trade_qty,
                executed_at=datetime.utcnow()
            )
            db_session.add(transaction)
            order = matching_order
        else:
            order = Order(
                user_id=user.id,
                instrument_id=instrument.id,
                order_type=OrderType.limit,
                direction=body.direction,
                price=body.price,
                quantity=qty,
                filled_quantity=0,
                status=OrderStatus.new,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db_session.add(order)

    return CreateOrderResponse(order_id=order.id, success=True)


async def get_orders(*, request: Request, db_session: AsyncSession = Depends(get_session)) -> List[LimitOrder | MarketOrder]:
    user = request.state.user

    result = await db_session.execute(
        select(Order, Instrument.ticker)
        .join(Instrument, Order.instrument_id == Instrument.id)
        .where(Order.user_id == user.id)
    )
    orders_db = result.all()

    orders = []
    for order, ticker in orders_db:
        body = LimitOrderBody(direction=Direction(order.direction), ticker=ticker, qty=order.quantity,
                              price=order.price) if order.order_type == OrderType.limit else MarketOrderBody(
            direction=Direction(order.direction), ticker=ticker, qty=int(order.quantity))
        order_model = LimitOrder(
            id=order.id,
            status=OrderStatus(order.status),
            user_id=order.user_id,
            timestamp=order.created_at,
            body=body,
            filled=int(order.filled_quantity) if order.order_type == OrderType.limit else 0
        ) if order.order_type == OrderType.limit else MarketOrder(
            id=order.id,
            status=OrderStatus(order.status),
            user_id=order.user_id,
            timestamp=order.created_at,
            body=body
        )
        orders.append(order_model)

    return orders


async def get_order(*, order_id: UUID4, request: Request, db_session: AsyncSession = Depends(get_session)) -> LimitOrder | MarketOrder:
    user = request.state.user

    result = await db_session.execute(
        select(Order, Instrument.ticker)
        .join(Instrument, Order.instrument_id == Instrument.id)
        .where(Order.id == order_id, Order.user_id == user.id)
    )
    order_db = result.first()

    if not order_db:
        raise HTTPException(status_code=404, detail="Order not found or does not belong to user")

    order, ticker = order_db
    body = LimitOrderBody(direction=Direction(order.direction), ticker=ticker, qty=order.quantity,
                          price=order.price) if order.order_type == OrderType.limit else MarketOrderBody(
        direction=Direction(order.direction), ticker=ticker, qty=int(order.quantity))

    order_model = LimitOrder(
        id=order.id,
        status=OrderStatus(order.status),
        user_id=order.user_id,
        timestamp=order.created_at,
        body=body,
        filled=int(order.filled_quantity) if order.order_type == OrderType.limit else 0
    ) if order.order_type == OrderType.limit else MarketOrder(
        id=order.id,
        status=OrderStatus(order.status),
        user_id=order.user_id,
        timestamp=order.created_at,
        body=body
    )

    return order_model


async def get_orderbook(*, ticker: str, limit: int, db_session: AsyncSession = Depends(get_session)) -> L2OrderBook:
    instrument = await db_session.scalar(
        select(Instrument)
        .where(Instrument.ticker == ticker and Instrument.is_active == True)
    )

    if not instrument:
        raise HTTPException(status_code=404, detail="Ticker not found or delisted")

    result = await db_session.execute(
        select(Order.price, func.sum(Order.quantity - Order.filled_quantity).label("qty"))
        .where(Order.instrument_id == instrument.id, Order.status == OrderStatus.new)
        .group_by(Order.price, Order.direction)
        .order_by(
            Order.price.desc() if Order.direction == Direction.buy else Order.price.asc()
        )
        .limit(limit)
    )
    order_levels = result.all()

    bid_levels = [
                     Level(price=int(price), qty=int(qty))
                     for price, qty in order_levels if order_levels[0][1] == Direction.buy
                 ][:limit]
    ask_levels = [
                     Level(price=int(price), qty=int(qty))
                     for price, qty in order_levels if order_levels[0][1] == Direction.sell
                 ][:limit]

    return L2OrderBook(bid_levels=bid_levels, ask_levels=ask_levels)


async def cancel_order(*, order_id: UUID4, request: Request, db_session: AsyncSession = Depends(get_session)) -> Ok:
    user = request.state.user

    order = await db_session.scalar(
        select(Order).where(Order.id == order_id, Order.user_id == user.id)
    )
    if not order or order.status not in [OrderStatus.new, OrderStatus.partially_filled]:
        raise HTTPException(status_code=404 if not order else 400,
                            detail="Order not found, does not belong to user, or cannot be canceled")

    quote_instrument = await db_session.scalar(select(Instrument).where(Instrument.ticker == DEFAULT_TICKER))
    balances = {
        "instrument": await db_session.scalar(
            select(Balance).where(Balance.user_id == user.id, Balance.instrument_id == order.instrument_id)
        ) or Balance(user_id=user.id, instrument_id=order.instrument_id, amount=0, locked_amount=0),
        "quote": await db_session.scalar(
            select(Balance).where(Balance.user_id == user.id, Balance.instrument_id == quote_instrument.id)
        ) or Balance(user_id=user.id, instrument_id=quote_instrument.id, amount=0, locked_amount=0)
    }
    for balance in balances.values():
        db_session.add(balance)

    remaining_qty = order.quantity - order.filled_quantity
    locked_to_release = remaining_qty * order.price if order.direction == Direction.buy else remaining_qty
    target_balance = balances["quote"] if order.direction == Direction.buy else balances["instrument"]
    target_balance.locked_amount = max(0, target_balance.locked_amount - locked_to_release)

    order.status = OrderStatus.canceled
    order.updated_at = datetime.utcnow()
    db_session.add(order)

    transaction = Transaction(
        order_id=order.id,
        instrument_id=order.instrument_id,
        price=order.price,
        quantity=remaining_qty,
        executed_at=datetime.utcnow(),
    )
    db_session.add(transaction)

    await db_session.commit()

    return Ok(success=True)