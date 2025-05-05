from pydantic import BaseModel, constr, UUID4, Field

from src.core.enums import UserRole


class User(BaseModel):
    id: UUID4
    name: str
    role: UserRole
    api_key: str


class Instrument(BaseModel):
    name: str
    ticker: constr(regex=r'^[A-Z]{2,10}$')


class Ok(BaseModel):
    success: bool = Field(default=True, const=True)