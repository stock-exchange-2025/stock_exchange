from fastapi import APIRouter, Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.admin import service
from src.core.enums import ApiTags
from src.dependencies import get_session
from src.user.schemas import User

router = APIRouter()


@router.delete("/admin/user/{user_id}", tags=[ApiTags.ADMIN, ApiTags.USER], response_model=User)
async def delete_user(user_id: UUID4, request: Request = None, db_session: AsyncSession = Depends(get_session)):
    return await service.delete_user(user_id=user_id, request=request, db_session=db_session)