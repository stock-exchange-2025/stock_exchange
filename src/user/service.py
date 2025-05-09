import uuid
from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from pydantic import UUID4

from src.core.database import DbSession
from src.user import utils
from src.user.enums import UserRole
from src.user.models import User as UserDAL
from src.user.schemas import NewUser
from src.user.schemas import User as UserDTO
from src.user.utils import generate_api_key


def register_new_user(*, user: NewUser, db_session: DbSession) -> UserDTO:
    if db_session.query(UserDAL).filter_by(username=user.name).first() is not None:
        raise ValueError(f"User with username '{user.name}' already exists")

    key_id, api_key = generate_api_key()

    new_user = UserDAL(
        id=uuid.uuid4(),
        username=user.name,
        role=UserRole.user,
        api_key=key_id,
        created_at=datetime.now())

    db_session.add(new_user)
    db_session.commit()
    return UserDTO(id=new_user.id, name=new_user.username, role=UserRole.user, api_key=api_key)


def delete_user(*, user_id: UUID4, api_key: str | None, db_session: DbSession) -> UserDTO:
    if api_key is None:
        raise HTTPException(status_code=401, detail="Authorization header is missing")

    existing_user = db_session.query(UserDAL).filter_by(id=user_id).first()
    if existing_user is None:
        raise ValueError(f"User with id '{user_id}' doesn't exist")

    user_by_api_key = utils.get_user_by_api_key(api_key=api_key, db_session=db_session)

    if existing_user.id != user_by_api_key.id and user_by_api_key.role == UserRole.user:
        raise ValueError("You don't have permission to delete your account")

    db_session.delete(existing_user)
    db_session.commit()

    return UserDTO(id=user_id, name=existing_user.username, role=existing_user.role, api_key=existing_user.api_key)