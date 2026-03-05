"""Tests for JWT token creation and validation."""

import time

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
    JWTError,
)
import pytest


def test_access_token_roundtrip():
    token = create_access_token("user-42", extra={"role": "admin"})
    payload = decode_token(token)
    assert payload["sub"] == "user-42"
    assert payload["type"] == "access"
    assert payload["role"] == "admin"


def test_refresh_token_roundtrip():
    token = create_refresh_token("user-99")
    payload = decode_token(token)
    assert payload["sub"] == "user-99"
    assert payload["type"] == "refresh"


def test_invalid_token_raises():
    with pytest.raises(JWTError):
        decode_token("not-a-valid-token")


def test_password_hash_and_verify():
    plain = "SuperSecret123!"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed)
    assert not verify_password("wrong-password", hashed)


def test_different_subjects_different_tokens():
    t1 = create_access_token("alice")
    t2 = create_access_token("bob")
    assert t1 != t2
    assert decode_token(t1)["sub"] == "alice"
    assert decode_token(t2)["sub"] == "bob"
