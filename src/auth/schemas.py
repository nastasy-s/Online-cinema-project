import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator
from typing import Any

from src.auth.models import GenderEnum, UserGroupEnum


def validate_password_strength(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("Password must contain at least one special character")
    return password


class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_password_strength(value)


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class ChangePasswordSchema(BaseModel):
    old_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_password_strength(value)


class RequestPasswordResetSchema(BaseModel):
    email: EmailStr


class ConfirmPasswordResetSchema(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_password_strength(value)


class ResendActivationSchema(BaseModel):
    email: EmailStr


class UserProfileSchema(BaseModel):
    first_name: str | None
    last_name: str | None
    avatar: str | None
    gender: GenderEnum | None
    date_of_birth: datetime | None
    info: str | None

    model_config = {"from_attributes": True}


class UserResponseSchema(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime
    group: UserGroupEnum | None = None
    profile: UserProfileSchema | None = None

    model_config = {"from_attributes": True}

    @field_validator("group", mode="before")
    @classmethod
    def get_group_name(cls, v: Any) -> Any:
        if v is not None and not isinstance(v, UserGroupEnum):
            return getattr(v, "name", v)
        return v


class ChangeUserGroupSchema(BaseModel):
    user_id: int
    group: UserGroupEnum
