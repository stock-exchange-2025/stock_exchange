from enum import Enum


class OrderDirection(str, Enum):
    buy = "BUY"
    sell = "SELL"


class OrderStatus(str, Enum):
    new = "NEW"
    executed = "EXECUTED"
    partially_filled = "PARTIALLY_FILLED"
    canceled = "CANCELED"
