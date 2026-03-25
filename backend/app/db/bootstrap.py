from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.user import User
from app.services.security import hash_password


async def bootstrap_system_admin(session: AsyncSession) -> User:
    settings = get_settings()
    result = await session.execute(select(User).where(User.username == settings.admin_username))
    user = result.scalar_one_or_none()
    if user is not None:
        return user

    user = User(
        username=settings.admin_username,
        email=settings.admin_email,
        password_hash=hash_password(settings.admin_password),
        is_system_admin=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
