from pydantic import UUID4
from sqlalchemy.orm import Session

from src.user.schemas import User as UserDTO

from src.user.schemas import NewUser, User

db_session = Session

async def register_new_user(*, user: NewUser) -> UserDTO:
    pass

async def delete_user(*, user_id: UUID4) -> User:
    pass