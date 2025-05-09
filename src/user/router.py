from fastapi import APIRouter, Depends, Header
from pydantic import UUID4

from src.core.database import DbSession
from src.core.enums import ApiTags
from src.user import service
from src.user.schemas import NewUser, User


router = APIRouter()


@router.post("/public/register", tags=[ApiTags.PUBLIC], response_model=User)
def register(user: NewUser, db_session: DbSession):
    return service.register_new_user(user=user, db_session=db_session)


@router.delete("/admin/user/{user_id}", tags=[ApiTags.ADMIN, ApiTags.USER], response_model=User)
def delete_user(user_id: UUID4, db_session: DbSession, authorization: str | None = Header(None, convert_underscore=False)):
    return service.delete_user(user_id=user_id, api_key=authorization, db_session=db_session)