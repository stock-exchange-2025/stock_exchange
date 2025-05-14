from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.user.enums import UserRole
from src.user.models import User as UserDAL
from src.user.schemas import User as UserDTO


async def delete_user(*, user_id: UUID4, request: Request, db_session: AsyncSession) -> UserDTO:
    user = request.state.user

    if not user:
        raise HTTPException(status_code=500, detail="User not found.")

    existing_user = (await db_session.execute(select(UserDAL).where(UserDAL.id == user_id))).scalar_one_or_none()

    if existing_user is None:
        raise HTTPException(status_code=400, detail=f"User with id '{user_id}' doesn't exist.")

    if existing_user.id != user.id and user.role != UserRole.admin:
        raise HTTPException(status_code=400, detail="You don't have permission to delete specified user.")

    await db_session.delete(existing_user)
    await db_session.commit()

    return UserDTO(id=user_id, name=existing_user.username, role=existing_user.role, api_key=existing_user.api_key)