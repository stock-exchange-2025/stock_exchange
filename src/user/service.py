import uuid
from datetime import datetime

from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.user.enums import UserRole
from src.user.models import User as UserDAL
from src.user.schemas import User as UserDTO

from src.user.schemas import NewUser
from src.user.utils import generate_api_key


# TODO вынести в общий класс database.py + добавить асинхронщину
Session = sessionmaker(class_=AsyncSession)
session = Session()


async def register_new_user(*, user: NewUser) -> UserDTO:
    #if session.query(UserDAL).filter_by(username=user.name).exists():
    #    raise ValueError(f"User with username '{user.name}' already exists")

    auth_token = generate_api_key()

    new_user = UserDAL(
        id=uuid.uuid4(),
        username=user.name,
        role=UserRole.user,
        auth_token=auth_token,
        created_at=datetime.now())

    session.add(new_user)
    session.commit()

    return UserDTO(id=new_user.id, username=new_user.username, role=UserRole.user, api_key=auth_token)


# TODO уточнить кто может удалять твой аккаунт ADMIN и челик с таким же api_key?
async def delete_user(*, user_id: UUID4) -> UserDTO:
    if session.query(UserDAL).filter_by(id=user_id).count() == 0:
        raise ValueError(f"User with id '{user_id}' does not exist")

    existing_user = session.query(UserDAL).filter_by(id=user_id).first()
    session.delete(existing_user)
    session.commit()

    return UserDTO(id=user_id, username=existing_user.username, role=existing_user.role, api_key=existing_user.api_key)