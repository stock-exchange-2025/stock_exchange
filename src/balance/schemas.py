from typing import Dict

from pydantic import BaseModel


class BalanceResponse(BaseModel):
    __root__: Dict[str, int]