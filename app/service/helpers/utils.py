from base64 import b64encode, b64decode
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_hash(plain_text: str, hashed_text: str) -> bool:
    return pwd_context.verify(plain_text, hashed_text)


def get_hash(plain_text: str) -> str:
    return pwd_context.hash(plain_text)


def create_token(
    data: dict[str, Any],
    secret_key: str,
    minutes: int,
    algorithm: str,
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def encode_to_base64(user_agent: str) -> str:
    return b64encode(user_agent.encode()).decode()


def decode_from_base64(base_token: str) -> str:
    return b64decode(base_token).decode()
