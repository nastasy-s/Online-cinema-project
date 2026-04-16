import pytest
from src.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)


def test_hash_password():
    password = "Test1234!"
    hashed = hash_password(password)
    assert hashed != password
    assert len(hashed) > 0


def test_verify_password_correct():
    password = "Test1234!"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    password = "Test1234!"
    hashed = hash_password(password)
    assert verify_password("WrongPassword!", hashed) is False


def test_create_access_token():
    data = {"sub": "1"}
    token = create_access_token(data)
    assert token is not None
    assert isinstance(token, str)


def test_decode_access_token():
    data = {"sub": "1"}
    token = create_access_token(data)
    payload = decode_token(token)
    assert payload["sub"] == "1"
    assert payload["type"] == "access"


def test_create_refresh_token():
    data = {"sub": "1"}
    token = create_refresh_token(data)
    payload = decode_token(token)
    assert payload["sub"] == "1"
    assert payload["type"] == "refresh"


def test_decode_invalid_token():
    with pytest.raises(ValueError, match="Invalid or expired token"):
        decode_token("invalid.token.here")
