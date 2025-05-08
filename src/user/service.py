from pydantic import UUID4

from src.user.schemas import User as UserDTO

from src.user.schemas import NewUser, User


async def register_new_user(*, user: NewUser) -> UserDTO:
    pass

async def delete_user(*, user_id: UUID4) -> User:
    pass