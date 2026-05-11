from app.common.security import (
    create_access_token,
    decode_access_token,
    generate_salt,
    hash_password,
    verify_password,
)


def test_generate_salt_length() -> None:
    salt = generate_salt()
    assert isinstance(salt, str)
    assert len(salt) == 32  # 16 bytes as hex


def test_generate_salt_unique() -> None:
    salts = {generate_salt() for _ in range(100)}
    assert len(salts) == 100


def test_hash_and_verify() -> None:
    salt = generate_salt()
    hashed = hash_password("mysecretpassword", salt)
    assert isinstance(hashed, str)
    assert len(hashed) > 0
    assert hashed != salt
    assert verify_password("mysecretpassword", hashed, salt) is True


def test_hash_different_salts() -> None:
    salt1 = generate_salt()
    salt2 = generate_salt()
    hash1 = hash_password("samepassword", salt1)
    hash2 = hash_password("samepassword", salt2)
    assert hash1 != hash2


def test_verify_wrong_password() -> None:
    salt = generate_salt()
    hashed = hash_password("correct", salt)
    assert verify_password("wrong", hashed, salt) is False


def test_verify_wrong_salt() -> None:
    salt1 = generate_salt()
    salt2 = generate_salt()
    hashed = hash_password("password", salt1)
    assert verify_password("password", hashed, salt2) is False


def test_create_and_decode_access_token() -> None:
    subject = "test-user-id"
    token = create_access_token(subject)
    assert isinstance(token, str)
    assert len(token) > 0

    decoded = decode_access_token(token)
    assert decoded == subject


def test_decode_invalid_token() -> None:
    assert decode_access_token("invalid-token") is None
    assert decode_access_token("") is None
