import pytest
from fastapi import HTTPException

from app.api.auth import login, read_current_user
from app.models.auth import LoginRequest


def test_login_and_me_flow(monkeypatch):
    monkeypatch.setenv("TRAVEL_ASSISTANT_AUTH_USERNAME", "alice")
    monkeypatch.setenv("TRAVEL_ASSISTANT_AUTH_PASSWORD", "secret")
    monkeypatch.setenv("TRAVEL_ASSISTANT_AUTH_DISPLAY_NAME", "Alice")
    monkeypatch.setenv("TRAVEL_ASSISTANT_AUTH_SECRET", "test-secret")
    monkeypatch.setenv("TRAVEL_ASSISTANT_AUTH_TTL_DAYS", "1")

    login_response = login(LoginRequest(username="alice", password="secret"))

    assert login_response.token_type == "bearer"
    assert login_response.user.username == "alice"
    assert login_response.user.display_name == "Alice"

    me_response = read_current_user(
        authorization=f"Bearer {login_response.access_token}",
    )

    assert me_response.username == "alice"
    assert me_response.display_name == "Alice"


def test_login_rejects_invalid_password(monkeypatch):
    monkeypatch.setenv("TRAVEL_ASSISTANT_AUTH_USERNAME", "alice")
    monkeypatch.setenv("TRAVEL_ASSISTANT_AUTH_PASSWORD", "secret")

    with pytest.raises(HTTPException) as exc_info:
        login(LoginRequest(username="alice", password="wrong"))

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "账号或密码错误"


def test_me_rejects_missing_token():
    with pytest.raises(HTTPException) as exc_info:
        read_current_user(authorization=None)

    assert exc_info.value.status_code == 401
