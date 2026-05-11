import secrets
from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt  # type: ignore[import-untyped]

from app.common.config import settings


def generate_salt() -> str:
    return secrets.token_hex(16)


def hash_password(password: str, salt: str) -> str:
    return bcrypt.hashpw(
        (salt + password).encode(),
        bcrypt.gensalt(),
    ).decode()


def verify_password(password: str, hashed: str, salt: str) -> bool:
    return bcrypt.checkpw((salt + password).encode(), hashed.encode())


def create_access_token(subject: str) -> str:
    expire = datetime.now(UTC) + timedelta(
        minutes=settings.access_token_expire_minutes,
    )
    return str(
        jwt.encode(
            {"sub": subject, "exp": expire},
            settings.secret_key,
            algorithm="HS256",
        ),
    )


def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return str(payload["sub"])
    except JWTError:
        return None
