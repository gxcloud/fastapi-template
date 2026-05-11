from pydantic import ValidationError

from app.domains.identity.schemas import UserCreate


def _validate(**kwargs) -> list[dict]:
    try:
        UserCreate(**kwargs)
        return []
    except ValidationError as e:
        return e.errors()


async def test_password_missing_uppercase() -> None:
    errors = _validate(email="test@example.com", password="lowercase1")
    assert any("uppercase" in str(e["msg"]) for e in errors)


async def test_password_missing_lowercase() -> None:
    errors = _validate(email="test@example.com", password="UPPERCASE1")
    assert any("lowercase" in str(e["msg"]) for e in errors)


async def test_password_missing_digit() -> None:
    errors = _validate(email="test@example.com", password="NoDigitsA")
    assert any("digit" in str(e["msg"]) for e in errors)


async def test_password_valid() -> None:
    u = UserCreate(email="test@example.com", password="ValidPass1")
    assert u.password == "ValidPass1"


async def test_password_none_for_oidc() -> None:
    u = UserCreate(email="test@example.com", oidc_sub="sub", oidc_provider="google")
    assert u.password is None
