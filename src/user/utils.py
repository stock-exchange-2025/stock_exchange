import hashlib
import hmac
import uuid

from passlib.context import CryptContext

SECRET = b"some_secret"


def generate_api_key() -> str:
    key_id = uuid.uuid4().hex
    signature = hmac.new(SECRET, key_id.encode(), hashlib.sha256).hexdigest()
    return f"{key_id}.{signature}"