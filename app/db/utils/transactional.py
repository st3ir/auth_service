from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def transaction(s: AsyncSession):

    await s.begin_nested()

    try:
        yield s
        await s.commit()

    except Exception as e:
        await s.rollback()
        raise e
