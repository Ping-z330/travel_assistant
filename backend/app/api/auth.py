from fastapi import APIRouter, Header, HTTPException, status

from app.models.auth import AuthTokenResponse, AuthUser, LoginRequest
from app.services.auth_service import build_login_response, decode_auth_token, verify_credentials

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=AuthTokenResponse)
def login(request: LoginRequest) -> AuthTokenResponse:
    user = verify_credentials(request)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误",
        )

    return build_login_response(user)


@router.get("/me", response_model=AuthUser)
def read_current_user(
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> AuthUser:
    token = _extract_bearer_token(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或登录已过期",
        )

    try:
        return decode_auth_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或登录已过期",
        ) from exc


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None

    prefix = "Bearer "
    if not authorization.startswith(prefix):
        return None

    token = authorization[len(prefix) :].strip()
    return token or None
