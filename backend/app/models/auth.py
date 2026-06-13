from typing import Literal

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=128)


class AuthUser(BaseModel):
    username: str
    display_name: str


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user: AuthUser
