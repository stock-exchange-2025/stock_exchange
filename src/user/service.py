import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.user.enums import UserRole
from src.user.models import User as UserDAL
from src.user.schemas import NewUser
from src.user.schemas import User as UserDTO
from src.user.utils import generate_api_key


async def create_user(*, user: NewUser, db_session: AsyncSession) -> UserDTO:
    existing_user = (await db_session.execute(select(UserDAL).where(UserDAL.username == user.name))).scalar_one_or_none()

    if existing_user is not None:
        raise ValueError(f"User with username '{user.name}' already exists.")

    key_id, api_key = generate_api_key()

    new_user = UserDAL(
        id=uuid.uuid4(),
        username=user.name,
        role=UserRole.admin,
        api_key=key_id,
        created_at=datetime.now())

    db_session.add(new_user)
    await db_session.commit()

    return UserDTO(id=new_user.id, name=new_user.username, role=new_user.role, api_key=api_key)