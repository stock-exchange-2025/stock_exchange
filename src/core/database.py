import logging

from fastapi import HTTPException
from sqlalchemy import make_url
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import Session, declarative_base
from starlette.requests import Request

from src import config

log = logging.getLogger(__name__)

Base = declarative_base()
DbSession = Session

def create_db_engine(connection_string: str):
    timeout_kwargs = {
        "pool_timeout": config.DATABASE_ENGINE_POOL_TIMEOUT,
        "pool_recycle": config.DATABASE_ENGINE_POOL_RECYCLE,
        "pool_size": config.DATABASE_ENGINE_POOL_SIZE,
        "max_overflow": config.DATABASE_ENGINE_MAX_OVERFLOW,
        "pool_pre_ping": config.DATABASE_ENGINE_POOL_PING,
    }

    return create_async_engine(make_url(connection_string), **timeout_kwargs)


db_engine = create_db_engine(config.SQLALCHEMY_DATABASE_URI)


def get_db(request: Request) -> DbSession:
    if not hasattr(request.state, "db"):
        raise HTTPException(status_code=500, detail="Database session is not initialized.")

    return request.state.db