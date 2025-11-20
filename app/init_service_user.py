import asyncio
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from db.utils.transactional import transaction
from service.helpers import utils
from service.roles.models import Role, UserRole
from service.roles.types import RoleType
from service.users.models import User
from settings import main_settings as m_s


async def init_service_user():

    async for session in get_db():
        session: AsyncSession

        query = (
            select(User)
            .where(User.email == m_s.SERVICE_USER_EMAIL)
        )

        user = await session.execute(query)
        user = user.scalar()
        if user:
            continue

        pass_salt = uuid4().hex
        user = User(
            first_name="SERVICE_USER",
            last_name="SERVICE_USER",
            parent_name="SERVICE_USER",
            pass_salt=pass_salt,
            password=utils.get_hash(m_s.SERVICE_USER_PASS + pass_salt),
            email=m_s.SERVICE_USER_EMAIL,
            active=True,
        )

        query = (
            select(Role)
            .where(Role.rolename == RoleType.SERVICE_USER)
        )
        role = await session.execute(query)
        role = role.scalar()

        async with transaction(session):
            session.add(user)

        await session.refresh(user)

        user_role = UserRole(user_id=user.id, role_id=role.id)
        async with transaction(session):
            session.add(user_role)


if __name__ == "__main__":
    asyncio.run(init_service_user())
