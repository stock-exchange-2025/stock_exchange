from enum import Enum


class UserRole(str, Enum):
    user = "USER"
    admin = "ADMIN"


class ApiTags(str, Enum):
    PUBLIC = "public"
    BALANCE = "balance"
    ORDER = "order"
    ADMIN = "admin"
    USER = "user"