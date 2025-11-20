from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from settings import postgres_settings


engine = create_async_engine(postgres_settings.DATABASE_URL, future=True, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator:
    try:
        session: AsyncSession = async_session()
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
    finally:
        await session.close()
