from fastapi import APIRouter, Depends
from pydantic import UUID4
from starlette.requests import Request

from src.core.database import get_db, DbSession
from src.core.enums import ApiTags
from src.user import service
from src.user.schemas import NewUser, User


router = APIRouter()


@router.post("/public/register", tags=[ApiTags.PUBLIC], response_model=User)
def register(user: NewUser, db_session: DbSession = Depends(get_db)):
    return service.register_new_user(user=user, db_session=db_session)


@router.delete("/admin/user/{user_id}", tags=[ApiTags.ADMIN, ApiTags.USER], response_model=User)
def delete_user(user_id: UUID4, request: Request = None, db_session: DbSession = Depends(get_db)):
    return service.delete_user(user_id=user_id, request=request, db_session=db_session)