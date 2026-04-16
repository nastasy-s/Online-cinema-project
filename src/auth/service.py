import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.auth.models import (
    ActivationToken,
    PasswordResetToken,
    RefreshToken,
    User,
    UserGroup,
    UserGroupEnum,
    UserProfile,
)
from src.auth.schemas import (
    ChangePasswordSchema,
    ConfirmPasswordResetSchema,
    UserRegisterSchema,
)
from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class AuthService:

    async def register(
        self, db: AsyncSession, data: UserRegisterSchema
    ) -> User:
        # Check email uniqueness
        result = await db.execute(select(User).where(User.email == data.email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise ValueError("User with this email already exists")

        # Get default user group
        result = await db.execute(
            select(UserGroup).where(UserGroup.name == UserGroupEnum.USER)
        )
        user_group = result.scalar_one_or_none()

        # Create user
        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            is_active=False,
            group_id=user_group.id if user_group else None,
        )
        db.add(user)
        await db.flush()

        # Create profile
        profile = UserProfile(user_id=user.id)
        db.add(profile)

        # Create activation token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        activation_token = ActivationToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at,
        )
        db.add(activation_token)
        await db.commit()
        await db.refresh(user)

        return user

    async def activate_account(
        self, db: AsyncSession, token: str
    ) -> User:
        result = await db.execute(
            select(ActivationToken).where(ActivationToken.token == token)
        )
        activation_token = result.scalar_one_or_none()

        if not activation_token:
            raise ValueError("Invalid activation token")

        if activation_token.expires_at < datetime.now(timezone.utc):
            raise ValueError("Activation token has expired")

        result = await db.execute(
            select(User).where(User.id == activation_token.user_id)
        )
        user = result.scalar_one_or_none()
        user.is_active = True

        await db.delete(activation_token)
        await db.commit()

        return user

    async def resend_activation(
        self, db: AsyncSession, email: str
    ) -> str:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or user.is_active:
            raise ValueError("User not found or already active")

        # Delete old token
        result = await db.execute(
            select(ActivationToken).where(ActivationToken.user_id == user.id)
        )
        old_token = result.scalar_one_or_none()
        if old_token:
            await db.delete(old_token)

        # Create new token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        new_token = ActivationToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at,
        )
        db.add(new_token)
        await db.commit()

        return token

    async def login(
        self, db: AsyncSession, email: str, password: str
    ) -> dict:
        result = await db.execute(
            select(User)
            .where(User.email == email)
            .options(selectinload(User.group))
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("Account is not activated")

        # Create tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        # Save refresh token
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        db_refresh_token = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at,
        )
        db.add(db_refresh_token)
        await db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def logout(
        self, db: AsyncSession, refresh_token: str
    ) -> None:
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token == refresh_token)
        )
        token = result.scalar_one_or_none()
        if token:
            await db.delete(token)
            await db.commit()

    async def refresh_access_token(
        self, db: AsyncSession, refresh_token: str
    ) -> dict:
        try:
            payload = decode_token(refresh_token)
        except ValueError:
            raise ValueError("Invalid refresh token")

        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")

        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token == refresh_token)
        )
        db_token = result.scalar_one_or_none()

        if not db_token:
            raise ValueError("Refresh token not found")

        if db_token.expires_at < datetime.now(timezone.utc):
            raise ValueError("Refresh token has expired")

        user_id = payload.get("sub")
        access_token = create_access_token({"sub": user_id})

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

    async def change_password(
        self, db: AsyncSession, user: User, data: ChangePasswordSchema
    ) -> None:
        if not verify_password(data.old_password, user.hashed_password):
            raise ValueError("Old password is incorrect")

        user.hashed_password = hash_password(data.new_password)
        await db.commit()

    async def request_password_reset(
        self, db: AsyncSession, email: str
    ) -> str:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise ValueError("User not found or not active")

        # Delete old token
        result = await db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.user_id == user.id
            )
        )
        old_token = result.scalar_one_or_none()
        if old_token:
            await db.delete(old_token)

        # Create new token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at,
        )
        db.add(reset_token)
        await db.commit()

        return token

    async def confirm_password_reset(
        self, db: AsyncSession, data: ConfirmPasswordResetSchema
    ) -> None:
        result = await db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token == data.token
            )
        )
        reset_token = result.scalar_one_or_none()

        if not reset_token:
            raise ValueError("Invalid reset token")

        if reset_token.expires_at < datetime.now(timezone.utc):
            raise ValueError("Reset token has expired")

        result = await db.execute(
            select(User).where(User.id == reset_token.user_id)
        )
        user = result.scalar_one_or_none()
        user.hashed_password = hash_password(data.new_password)

        await db.delete(reset_token)
        await db.commit()


auth_service = AuthService()
