from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.auth.schemas import (
    ChangePasswordSchema,
    ChangeUserGroupSchema,
    ConfirmPasswordResetSchema,
    RefreshTokenSchema,
    RequestPasswordResetSchema,
    ResendActivationSchema,
    TokenSchema,
    UserLoginSchema,
    UserRegisterSchema,
    UserResponseSchema,
)
from src.auth.service import auth_service
from src.core.database import get_db
from src.core.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a new user account and sends an activation email.",
)
async def register(
    data: UserRegisterSchema,
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await auth_service.register(db, data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/activate/{token}",
    summary="Activate user account",
    description="Activates a user account using the token sent to email.",
)
async def activate_account(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        await auth_service.activate_account(db, token)
        return {"message": "Account activated successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/resend-activation",
    summary="Resend activation email",
    description="Resends the activation token to the user's email.",
)
async def resend_activation(
    data: ResendActivationSchema,
    db: AsyncSession = Depends(get_db),
):
    try:
        await auth_service.resend_activation(db, data.email)
        return {"message": "Activation email sent successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=TokenSchema,
    summary="Login",
    description="Authenticates user and returns JWT access and refresh tokens.",
)
async def login(
    data: UserLoginSchema,
    db: AsyncSession = Depends(get_db),
):
    try:
        tokens = await auth_service.login(db, data.email, data.password)
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post(
    "/logout",
    summary="Logout",
    description="Invalidates the refresh token so it cannot be used again.",
)
async def logout(
    data: RefreshTokenSchema,
    db: AsyncSession = Depends(get_db),
):
    await auth_service.logout(db, data.refresh_token)
    return {"message": "Logged out successfully"}


@router.post(
    "/refresh",
    summary="Refresh access token",
    description="Uses the refresh token to issue a new access token.",
)
async def refresh_token(
    data: RefreshTokenSchema,
    db: AsyncSession = Depends(get_db),
):
    try:
        tokens = await auth_service.refresh_access_token(db, data.refresh_token)
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post(
    "/change-password",
    summary="Change password",
    description="Changes the password for the currently authenticated user.",
)
async def change_password(
    data: ChangePasswordSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        await auth_service.change_password(db, current_user, data)
        return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/password-reset/request",
    summary="Request password reset",
    description="Sends a password reset token to the user's email.",
)
async def request_password_reset(
    data: RequestPasswordResetSchema,
    db: AsyncSession = Depends(get_db),
):
    try:
        await auth_service.request_password_reset(db, data.email)
        return {"message": "Password reset email sent"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/password-reset/confirm",
    summary="Confirm password reset",
    description="Sets a new password using the reset token received by email.",
)
async def confirm_password_reset(
    data: ConfirmPasswordResetSchema,
    db: AsyncSession = Depends(get_db),
):
    try:
        await auth_service.confirm_password_reset(db, data)
        return {"message": "Password reset successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/me",
    response_model=UserResponseSchema,
    summary="Get current user",
    description="Returns the profile of the currently authenticated user.",
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.put(
    "/admin/change-group",
    summary="Change user group",
    description="Admin only. Changes the group (role) of a user.",
)
async def change_user_group(
    data: ChangeUserGroupSchema,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    try:
        await auth_service.change_user_group(db, data)
        return {"message": "User group changed successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
