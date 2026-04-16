from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.auth.models import UserGroup, UserGroupEnum


async def seed_user_groups(db: AsyncSession) -> None:
    for group_name in UserGroupEnum:
        result = await db.execute(
            select(UserGroup).where(UserGroup.name == group_name)
        )
        existing = result.scalar_one_or_none()
        if not existing:
            group = UserGroup(name=group_name)
            db.add(group)
    await db.commit()
