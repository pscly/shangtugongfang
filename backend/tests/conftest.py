import os
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("JWT_SECRET", "test-secret-for-shangtugongfang-32-bytes")
os.environ.setdefault("ADMIN_USERNAME", "sysadmin")
os.environ.setdefault("ADMIN_PASSWORD", "Admin12345!")
os.environ.setdefault("ADMIN_EMAIL", "admin@example.com")

from app.main import create_app
from app.db.bootstrap import bootstrap_system_admin
from app.db.session import async_session_factory, engine
from app.models.base import Base


@pytest.fixture(autouse=True)
async def reset_db() -> AsyncIterator[None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_factory() as session:
        await bootstrap_system_admin(session)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
async def client() -> AsyncIterator[AsyncClient]:
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        yield ac


@pytest.fixture()
async def db_session():
    async with async_session_factory() as session:
        yield session
