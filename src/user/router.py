from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import ApiTags
from src.dependencies import get_session
from src.user import service
from src.user.schemas import NewUser, User

router = APIRouter()


@router.post("/public/register", tags=[ApiTags.PUBLIC], response_model=User)
async def register(user: NewUser, db_session: AsyncSession = Depends(get_session)):
    return await service.create_user(user=user, db_session=db_session)