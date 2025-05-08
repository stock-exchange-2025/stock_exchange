from typing import Optional

from fastapi import APIRouter, Header
from pydantic import UUID4

from src.core.enums import ApiTags
from src.user import service
from src.user.schemas import NewUser, User

router = APIRouter()


@router.post("/public/register", tags=[ApiTags.PUBLIC], response_model=User)
async def register(user: NewUser):
    return await service.register_new_user(user=user)

@router.delete("/admin/user/{user_id}", tags=[ApiTags.ADMIN, ApiTags.USER], response_model=User)
async def delete_user(user_id: UUID4, authorization: Optional[str] = Header(None)):
    return await service.delete_user(user_id=user_id)