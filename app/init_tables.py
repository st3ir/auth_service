import asyncio

from sqlalchemy import exists, insert, literal, select

from db.session import async_session
from service.roles.models import Role
from service.roles.types import RoleType


async def init_role_table():
    async with async_session() as session:

        for role in [x.value for x in RoleType]:
            subq = select(literal(role)).where(
                ~exists().where(Role.rolename == role)
            )
            query = insert(Role).from_select(['rolename'], subq)
            await session.execute(query)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(init_role_table())
