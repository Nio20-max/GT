"""Auth routes – register, login, refresh, logout."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
    JWTError,
)
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    RefreshRequest,
    TokenResponse,
)
from app.schemas.common import ok, err

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(body: RegisterRequest):
    """Register a new user and club.

    Full implementation will persist the user via the database session.
    """
    hashed = hash_password(body.password)
    # TODO: persist user + club via DB session
    tokens = TokenResponse(
        access_token=create_access_token(body.username),
        refresh_token=create_refresh_token(body.username),
    )
    return ok(tokens.model_dump())


@router.post("/login")
async def login(body: LoginRequest):
    """Authenticate and return tokens.

    Full implementation will look up the user and verify the password hash.
    """
    # TODO: look up user in DB and verify password
    tokens = TokenResponse(
        access_token=create_access_token(body.username),
        refresh_token=create_refresh_token(body.username),
    )
    return ok(tokens.model_dump())


@router.post("/refresh")
async def refresh(body: RefreshRequest):
    """Issue new access token from a valid refresh token."""
    try:
        payload = decode_token(body.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    new_access = create_access_token(payload["sub"])
    return ok({"access_token": new_access, "token_type": "bearer"})


@router.post("/logout")
async def logout():
    """Invalidate session (no-op until session table wiring)."""
    return ok({"message": "Logged out"})
