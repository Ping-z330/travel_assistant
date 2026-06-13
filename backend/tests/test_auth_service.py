from app.models.auth import AuthUser, LoginRequest
from app.services.auth_service import create_auth_token, decode_auth_token, verify_credentials


def test_verify_credentials_accepts_configured_account(monkeypatch):
    monkeypatch.setenv("TRAVEL_ASSISTANT_AUTH_USERNAME", "alice")
    monkeypatch.setenv("TRAVEL_ASSISTANT_AUTH_PASSWORD", "secret")
    monkeypatch.setenv("TRAVEL_ASSISTANT_AUTH_DISPLAY_NAME", "Alice")

    user = verify_credentials(LoginRequest(username="alice", password="secret"))

    assert user == AuthUser(username="alice", display_name="Alice")


def test_verify_credentials_rejects_wrong_password(monkeypatch):
    monkeypatch.setenv("TRAVEL_ASSISTANT_AUTH_USERNAME", "alice")
    monkeypatch.setenv("TRAVEL_ASSISTANT_AUTH_PASSWORD", "secret")

    user = verify_credentials(LoginRequest(username="alice", password="wrong"))

    assert user is None


def test_create_and_decode_auth_token(monkeypatch):
    monkeypatch.setenv("TRAVEL_ASSISTANT_AUTH_SECRET", "test-secret")
    monkeypatch.setenv("TRAVEL_ASSISTANT_AUTH_TTL_DAYS", "1")

    token = create_auth_token(AuthUser(username="alice", display_name="Alice"))

    assert decode_auth_token(token) == AuthUser(username="alice", display_name="Alice")
