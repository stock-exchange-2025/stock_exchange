from pydantic import BaseModel

from src.core.enums import Role


class User(BaseModel):
    id: str
    name: str
    role: Role
    api_key: str


class Instrument(BaseModel):
    name: str
    ticker: str


class Ok(BaseModel):
    success: bool = True