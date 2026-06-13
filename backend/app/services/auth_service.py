from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from app.models.auth import AuthTokenResponse, AuthUser, LoginRequest

AUTH_USERNAME_ENV = "TRAVEL_ASSISTANT_AUTH_USERNAME"
AUTH_PASSWORD_ENV = "TRAVEL_ASSISTANT_AUTH_PASSWORD"
AUTH_DISPLAY_NAME_ENV = "TRAVEL_ASSISTANT_AUTH_DISPLAY_NAME"
AUTH_SECRET_ENV = "TRAVEL_ASSISTANT_AUTH_SECRET"
AUTH_TTL_DAYS_ENV = "TRAVEL_ASSISTANT_AUTH_TTL_DAYS"

DEFAULT_USERNAME = "demo"
DEFAULT_PASSWORD = "travel123"
DEFAULT_DISPLAY_NAME = "旅行助手用户"
DEFAULT_SECRET = "travel-assistant-dev-secret"
DEFAULT_TTL_DAYS = 7


def verify_credentials(request: LoginRequest) -> AuthUser | None:
    account = get_demo_account()
    if request.username.strip() != account.username:
        return None

    if request.password != account.password:
        return None

    return AuthUser(username=account.username, display_name=account.display_name)


def create_auth_token(user: AuthUser) -> str:
    issued_at = datetime.now(timezone.utc)
    expires_at = issued_at + timedelta(days=get_token_ttl_days())
    payload = {
        "sub": user.username,
        "display_name": user.display_name,
        "iat": int(issued_at.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_token = _base64url_encode(payload_bytes)
    signature = hmac.new(
        get_auth_secret().encode("utf-8"),
        payload_bytes,
        hashlib.sha256,
    ).digest()
    signature_token = _base64url_encode(signature)
    return f"{payload_token}.{signature_token}"


def decode_auth_token(token: str) -> AuthUser:
    try:
        payload_token, signature_token = token.split(".", 1)
    except ValueError as exc:
        raise ValueError("invalid token format") from exc

    payload_bytes = _base64url_decode(payload_token)
    expected_signature = hmac.new(
        get_auth_secret().encode("utf-8"),
        payload_bytes,
        hashlib.sha256,
    ).digest()
    actual_signature = _base64url_decode(signature_token)

    if not hmac.compare_digest(expected_signature, actual_signature):
        raise ValueError("invalid token signature")

    payload = json.loads(payload_bytes.decode("utf-8"))
    _assert_token_not_expired(payload)

    return AuthUser(
        username=str(payload["sub"]),
        display_name=str(payload["display_name"]),
    )


def build_login_response(user: AuthUser) -> AuthTokenResponse:
    return AuthTokenResponse(access_token=create_auth_token(user), user=user)


@dataclass(frozen=True)
class DemoAccount:
    username: str
    password: str
    display_name: str


def get_demo_account() -> DemoAccount:
    return DemoAccount(
        username=os.getenv(AUTH_USERNAME_ENV, DEFAULT_USERNAME).strip() or DEFAULT_USERNAME,
        password=os.getenv(AUTH_PASSWORD_ENV, DEFAULT_PASSWORD),
        display_name=os.getenv(AUTH_DISPLAY_NAME_ENV, DEFAULT_DISPLAY_NAME).strip()
        or DEFAULT_DISPLAY_NAME,
    )


def get_auth_secret() -> str:
    return os.getenv(AUTH_SECRET_ENV, DEFAULT_SECRET)


def get_token_ttl_days() -> int:
    raw_value = os.getenv(AUTH_TTL_DAYS_ENV, str(DEFAULT_TTL_DAYS))
    try:
        ttl_days = int(raw_value)
    except ValueError:
        return DEFAULT_TTL_DAYS

    return ttl_days if ttl_days > 0 else DEFAULT_TTL_DAYS


def _assert_token_not_expired(payload: dict[str, Any]) -> None:
    expires_at = int(payload.get("exp", 0))
    now = int(datetime.now(timezone.utc).timestamp())
    if expires_at <= now:
        raise ValueError("token expired")


def _base64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("utf-8")


def _base64url_decode(token: str) -> bytes:
    padding = "=" * (-len(token) % 4)
    return base64.urlsafe_b64decode(f"{token}{padding}".encode("utf-8"))
