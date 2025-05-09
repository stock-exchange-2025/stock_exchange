import os
from urllib import parse

from starlette.config import Config
from starlette.datastructures import Secret


def get_env_tags(tag_list: list[str]) -> dict:
    """Create a dictionary of available env tags."""
    tags = {}
    for t in tag_list:
        tag_key, env_key = t.split(":")

        env_value = os.environ.get(env_key)

        if env_value:
            tags.update({tag_key: env_value})

    return tags


config = Config(".env")

DATABASE_HOSTNAME = config("DATABASE_HOSTNAME")
DATABASE_CREDENTIALS = config("DATABASE_CREDENTIALS", cast=Secret)

_DATABASE_CREDENTIAL_USER, _DATABASE_CREDENTIAL_PASSWORD = str(DATABASE_CREDENTIALS).split(":")
_QUOTED_DATABASE_PASSWORD = parse.quote(str(_DATABASE_CREDENTIAL_PASSWORD))

DATABASE_NAME = config("DATABASE_NAME", default="stock_exchange")
DATABASE_PORT = config("DATABASE_PORT", default="5432")

SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{_DATABASE_CREDENTIAL_USER}:{_QUOTED_DATABASE_PASSWORD}@{DATABASE_HOSTNAME}:{DATABASE_PORT}/{DATABASE_NAME}"

DATABASE_ENGINE_MAX_OVERFLOW = config("DATABASE_ENGINE_MAX_OVERFLOW", cast=int, default=10)
# Deal with DB disconnects
# https://docs.sqlalchemy.org/en/20/core/pooling.html#pool-disconnects
DATABASE_ENGINE_POOL_PING = config("DATABASE_ENGINE_POOL_PING", default=False)
DATABASE_ENGINE_POOL_RECYCLE = config("DATABASE_ENGINE_POOL_RECYCLE", cast=int, default=3600)
DATABASE_ENGINE_POOL_SIZE = config("DATABASE_ENGINE_POOL_SIZE", cast=int, default=20)
DATABASE_ENGINE_POOL_TIMEOUT = config("DATABASE_ENGINE_POOL_TIMEOUT", cast=int, default=30)
