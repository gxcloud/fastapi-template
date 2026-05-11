from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt  # type: ignore[import-untyped]
from passlib.context import CryptContext  # type: ignore[import-untyped]

from app.common.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain: str, hashed: str) -> bool:
    return bool(pwd_context.verify(plain, hashed))


def hash_password(password: str) -> str:
    return str(pwd_context.hash(password))


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
