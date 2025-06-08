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

    # Шаг 1: Получаем инструмент
    instrument = await db_session.scalar(
        select(Instrument).where(Instrument.ticker == body.ticker)
    )
    if instrument is None or instrument.delisted:
        raise HTTPException(status_code=404, detail="Ticker not found or delisted")

    # Шаг 2: Получаем базовый инструмент (RUB)
    quote_instrument = await db_session.scalar(
        select(Instrument).where(Instrument.ticker == DEFAULT_TICKER)
    )
    if quote_instrument is None:
        raise HTTPException(status_code=500, detail="RUB instrument not found")

    # Шаг 3: Получаем балансы текущего пользователя
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

    # Шаг 4: Проверяем и резервируем средства/актив
    qty = body.qty
    price = body.price if isinstance(body, LimitOrderBody) else 0

    required = qty * price if body.direction == Direction.buy and isinstance(body, LimitOrderBody) else qty
    available = (balances["quote"].amount - balances["quote"].locked_amount) if body.direction == Direction.buy else \
        (balances["instrument"].amount - balances["instrument"].locked_amount)
    if available < required:
        raise HTTPException(status_code=400,
                            detail=f"Недостаточно {'средств' if body.direction == Direction.buy else 'активов'}")

    if body.direction == Direction.buy and isinstance(body, LimitOrderBody):
        balances["quote"].locked_amount += Decimal(str(required))
    else:
        balances["instrument"].locked_amount += qty

    # Шаг 5: Обработка заявки Market
    order = None
    if isinstance(body, MarketOrderBody):
        # Создаём новую рыночную заявку с последней рыночной ценой
        last_market_price = 0
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
        if matching_order:
            last_market_price = matching_order.price  # Используем цену встречного ордера как пример
        order = Order(
            user_id=user.id,
            instrument_id=instrument.id,
            order_type=OrderType.market,
            direction=body.direction,
            price=last_market_price,
            quantity=qty,
            filled_quantity=0,
            status=OrderStatus.new,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(order)

        if matching_order:  # Если есть подходящий ордер, выполняем мэтчинг
            # Получаем балансы встречного пользователя
            matching_user_id = matching_order.user_id
            matching_balances = {
                "instrument": await db_session.scalar(
                    select(Balance).where(Balance.user_id == matching_user_id, Balance.instrument_id == instrument.id)
                ),
                "quote": await db_session.scalar(
                    select(Balance).where(Balance.user_id == matching_user_id,
                                          Balance.instrument_id == quote_instrument.id)
                )
            }
            for balance_type, balance in matching_balances.items():
                if balance is None:
                    balance = Balance(
                        user_id=matching_user_id,
                        instrument_id=instrument.id if balance_type == "instrument" else quote_instrument.id,
                        amount=0,
                        locked_amount=0
                    )
                    matching_balances[balance_type] = balance
                    db_session.add(balance)

            # Выполнение транзакции
            trade_price = matching_order.price
            trade_qty = min(qty, matching_order.quantity - matching_order.filled_quantity)
            if trade_qty == 0:
                raise HTTPException(status_code=400, detail="Нет доступного количества для торговли")

            order.filled_quantity += trade_qty
            matching_order.filled_quantity += trade_qty

            order.status = OrderStatus.executed if order.filled_quantity == order.quantity else OrderStatus.partially_filled
            matching_order.status = OrderStatus.executed if matching_order.filled_quantity == matching_order.quantity else \
                OrderStatus.partially_filled

            # 2 пункт TODO
            # Обновляем балансы текущего пользователя
            if body.direction == Direction.buy:
                balances["quote"].amount -= Decimal(str(trade_qty * trade_price))
                balances["quote"].locked_amount = 0
                balances["instrument"].amount += trade_qty

            else:
                balances["instrument"].amount -= trade_qty
                balances["instrument"].locked_amount = 0
                balances["quote"].amount += Decimal(str(trade_qty * trade_price))

            # 3 пункт TODO
            # Обновляем балансы встречного пользователя
            if body.direction == Direction.buy:
                matching_balances["instrument"].amount -= trade_qty
                matching_balances["instrument"].locked_amount = 0
                matching_balances["quote"].amount += Decimal(str(trade_qty * trade_price))
            else:
                matching_balances["quote"].amount -= Decimal(str(trade_qty * trade_price))
                matching_balances["quote"].locked_amount = 0
                matching_balances["instrument"].amount += trade_qty

            # Создаём транзакцию
            transaction = Transaction(
                order_id=order.id,
                instrument_id=instrument.id,
                price=trade_price,
                quantity=trade_qty,
                executed_at=datetime.utcnow()
            )
            db_session.add(transaction)
    else:  # Лимитная заявка
        # Создаём новую заявку
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

        # Ищем подходящий встречный ордер
        price_condition = Order.price <= body.price if body.direction == Direction.buy else Order.price >= body.price
        matching_order = await db_session.scalar(
            select(Order)
            .where(
                Order.instrument_id == instrument.id,
                Order.direction == (Direction.sell if body.direction == Direction.buy else Direction.buy),
                Order.status == OrderStatus.new,
                price_condition
            )
            .order_by(Order.price.asc() if body.direction == Direction.buy else Order.price.desc(),
                      Order.created_at.asc()).limit(1)
        )

        if matching_order:  # Если есть подходящий ордер, выполняем мэтчинг
            # Получаем балансы встречного пользователя
            matching_user_id = matching_order.user_id
            matching_balances = {
                "instrument": await db_session.scalar(
                    select(Balance).where(Balance.user_id == matching_user_id, Balance.instrument_id == instrument.id)
                ),
                "quote": await db_session.scalar(
                    select(Balance).where(Balance.user_id == matching_user_id,
                                          Balance.instrument_id == quote_instrument.id)
                )
            }
            for balance_type, balance in matching_balances.items():
                if balance is None:
                    balance = Balance(
                        user_id=matching_user_id,
                        instrument_id=instrument.id if balance_type == "instrument" else quote_instrument.id,
                        amount=0,
                        locked_amount=0
                    )
                    matching_balances[balance_type] = balance
                    db_session.add(balance)

            # Выполнение транзакции
            trade_price = matching_order.price if body.direction == Direction.buy else body.price
            trade_qty = min(qty, matching_order.quantity - matching_order.filled_quantity)
            if trade_qty == 0:
                raise HTTPException(status_code=400, detail="Нет доступного количества для торговли")

            # Обновляем обе заявки
            order.filled_quantity += trade_qty
            matching_order.filled_quantity += trade_qty

            order.status = OrderStatus.executed if order.filled_quantity == order.quantity else OrderStatus.partially_filled
            matching_order.status = OrderStatus.executed if matching_order.filled_quantity == matching_order.quantity else \
                OrderStatus.partially_filled

            # Обновляем балансы текущего пользователя
            if body.direction == Direction.buy:
                balances["quote"].amount -= Decimal(str(trade_qty * trade_price))
                balances["quote"].locked_amount = 0
                balances["instrument"].amount += trade_qty

            else:
                balances["instrument"].amount -= trade_qty
                balances["instrument"].locked_amount = 0
                balances["quote"].amount += Decimal(str(trade_qty * trade_price))

            # Обновляем балансы встречного пользователя
            if body.direction == Direction.buy:
                matching_balances["instrument"].amount -= trade_qty
                matching_balances["instrument"].locked_amount = 0
                matching_balances["quote"].amount += Decimal(str(trade_qty * trade_price))
            else:
                matching_balances["quote"].amount -= Decimal(str(trade_qty * trade_price))
                matching_balances["quote"].locked_amount = 0
                matching_balances["instrument"].amount += trade_qty

            # Создаём транзакцию
            transaction = Transaction(
                order_id=order.id,
                instrument_id=instrument.id,
                price=trade_price,
                quantity=trade_qty,
                executed_at=datetime.utcnow()
            )
            db_session.add(transaction)

    # Шаг 6: Фиксация изменений
    await db_session.commit()

    return CreateOrderResponse(order_id=order.id, status=True)


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
    instrument = await db_session.scalar(select(Instrument).where(Instrument.ticker == ticker))
    if not instrument or instrument.delisted:
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