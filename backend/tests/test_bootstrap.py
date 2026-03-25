import pytest
from sqlalchemy import select

from app.db.bootstrap import bootstrap_system_admin
from app.models.user import User


@pytest.mark.asyncio
async def test_bootstrap_system_admin_should_create_admin_from_env(db_session):
    user = await bootstrap_system_admin(db_session)

    assert user.username == "sysadmin"
    assert user.email == "admin@example.com"
    assert user.is_system_admin is True

    result = await db_session.execute(select(User))
    users = result.scalars().all()
    assert len(users) == 1


@pytest.mark.asyncio
async def test_bootstrap_system_admin_should_be_idempotent(db_session):
    first = await bootstrap_system_admin(db_session)
    second = await bootstrap_system_admin(db_session)

    assert first.id == second.id
