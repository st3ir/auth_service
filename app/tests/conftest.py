import pytest

import redis.asyncio as aioredis
from asyncio import current_task

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    async_scoped_session,
    create_async_engine
)
from sqlalchemy.pool import NullPool

from settings import test_postgres_settings, redis_settings
from service.auth import handlers

from db.session import get_db
from db.meta import Base
from main import app


engine_test = create_async_engine(
    test_postgres_settings.DATABASE_URL,
    poolclass=NullPool
)
async_session = async_sessionmaker(
    engine_test, expire_on_commit=False, class_=AsyncSession
)
factory_session = async_scoped_session(async_session, scopefunc=current_task)


async def override_get_db():
    async with async_session() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True, scope="function")
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture(scope="function")
async def fixture_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
async def fixture_mock_redis(monkeypatch):
    redis_cache = aioredis.from_url(redis_settings.REDIS_URL, decode_responses=True)
    monkeypatch.setattr(
        handlers, "redis", redis_cache
    )
    yield
    await redis_cache.close()
