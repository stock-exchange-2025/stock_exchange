from pydantic import BaseModel, constr


class Instrument(BaseModel):
    name: str
    ticker: constr(regex=r'^[A-Z]{2,10}$')