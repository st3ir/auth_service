from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from service.exceptions.api.users import InvalidUserRoleException
from service.roles.models import Role
from service.roles.types import RoleType


async def check_user_role_existence(
    db: AsyncSession = Depends(get_db),
    role: str | None = None,
) -> Role | None:
    if not role:
        return

    db_role = (
        await db.execute(select(Role).where(Role.rolename == role))
    ).scalar()

    if not db_role:
        raise InvalidUserRoleException()

    return db_role


async def get_default_user_role(db: AsyncSession) -> Role:

    return (
        await db.execute(select(Role).where(Role.rolename == RoleType.HR_EMPLOYEE))
    ).scalar()
