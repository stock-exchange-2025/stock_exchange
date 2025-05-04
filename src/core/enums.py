from enum import Enum


class Role(str, Enum):
    user = "USER"
    admin = "ADMIN"


class Ticker(str, Enum):
    memecoin = "MEMECOIN"


class ApiTags(str, Enum):
    PUBLIC = "public"
    BALANCE = "balance"
    ORDER = "order"
    ADMIN = "admin"
    USER = "user"