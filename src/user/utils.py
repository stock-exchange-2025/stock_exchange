import hashlib
import hmac
import uuid
from typing import Optional, Tuple

from fastapi import HTTPException
from sqlalchemy import select

from src import config
from src.core.database import DbSession
from src.user.models import User as UserDAL

TOKEN_PREFIX = "TOKEN"

def get_secret_key() -> str:
    secret_key = config.SECRET_KEY

    if secret_key is None:
        raise ValueError("SECRET_KEY environment variable is not set")

    return secret_key


def generate_api_key() -> Tuple[str, str]:
    key_id = uuid.uuid4().hex
    secret = get_secret_key()

    signature = hmac.new(str(secret).encode(), key_id.encode(), hashlib.sha256).hexdigest()
    full_api_key = f"{TOKEN_PREFIX} {key_id}.{signature}"

    return key_id, full_api_key


def get_user_by_api_key(api_key: Optional[str], db_session: DbSession) -> UserDAL:
    try:
        _, key_part = api_key.split(" ", 1)
        key_id, signature = key_part.split(".")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid API key")

    secret = get_secret_key()
    expected_sig = hmac.new(str(secret).encode(), key_id.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(signature, expected_sig):
        raise HTTPException(status_code=401, detail="Invalid API key")

    return db_session.execute(select(UserDAL).filter_by(api_key=key_id)).scalar_one_or_none()