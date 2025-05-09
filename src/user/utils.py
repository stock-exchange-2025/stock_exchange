import hashlib
import hmac
import uuid
from typing import Optional, Tuple

from sqlalchemy import select

from src import config
from src.core.database import DbSession
from src.user.models import User as UserDAL

TOKEN_PREFIX = "TOKEN"

def get_secret_key() -> str:
    secret_key = config.SQLALCHEMY_DATABASE_URI
    if secret_key is None:
        raise ValueError("SECRET_KEY environment variable is not set")
    return secret_key


def generate_api_key() -> Tuple[str, str]:
    key_id = uuid.uuid4().hex
    secret = get_secret_key()
    signature = hmac.new(secret.encode(), key_id.encode(), hashlib.sha256).hexdigest()
    full_api_key = f"{TOKEN_PREFIX} {key_id}.{signature}"
    return key_id, full_api_key


def get_user_by_api_key(api_key: Optional[str], db_session: DbSession) -> UserDAL:
    if api_key is None or not api_key.startswith(f"{TOKEN_PREFIX} "):
        raise ValueError(f"API key need contains '{TOKEN_PREFIX}' prefix")

    try:
        _, key_part = api_key.split(" ", 1)
        key_id, signature = key_part.split(".")
    except ValueError:
        raise ValueError("Invalid API key")
    secret = get_secret_key()

    expected_sig = hmac.new(secret.encode(), key_id.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected_sig):
        raise ValueError("Invalid API key")

    return db_session.execute(select(UserDAL).filter_by(api_key=key_id)).scalar_one_or_none()