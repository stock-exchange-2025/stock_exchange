import logging

from fastapi import HTTPException
from sqlalchemy import create_engine, make_url
from sqlalchemy.orm import Session, declarative_base
from starlette.requests import Request

from src import config

log = logging.getLogger(__name__)

Base = declarative_base()

DbSession = Session

def create_db_engine(connection_string: str):
    url = make_url(connection_string)

    # Use existing configuration values with fallbacks
    timeout_kwargs = {
        # Connection timeout - how long to wait for a connection from the pool
        "pool_timeout": config.DATABASE_ENGINE_POOL_TIMEOUT,
        # Recycle connections after this many seconds
        "pool_recycle": config.DATABASE_ENGINE_POOL_RECYCLE,
        # Maximum number of connections to keep in the pool
        "pool_size": config.DATABASE_ENGINE_POOL_SIZE,
        # Maximum overflow connections allowed beyond pool_size
        "max_overflow": config.DATABASE_ENGINE_MAX_OVERFLOW,
        # Connection pre-ping to verify connection is still alive
        "pool_pre_ping": config.DATABASE_ENGINE_POOL_PING,
    }
    return create_engine(url, **timeout_kwargs)


engine = create_db_engine(config.SQLALCHEMY_DATABASE_URI)
Base.metadata.create_all(engine)

def get_db(request: Request) -> DbSession:
    if not hasattr(request.state, "db"):
        raise HTTPException(status_code=500, detail="Database session not initialized")
    return request.state.db