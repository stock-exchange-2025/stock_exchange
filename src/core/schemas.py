from pydantic import BaseModel, Field


class Ok(BaseModel):
    success: bool = Field(default=True, const=True)