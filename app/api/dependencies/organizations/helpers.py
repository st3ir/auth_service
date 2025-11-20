from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from service.exceptions.api.organizations import DepartmentNotFoundException
from service.organizations.models import Department


async def get_department_if_exist(
    department_id: int,
    db: AsyncSession = Depends(get_db)
) -> Department:

    obj_exp = await db.execute(select(Department).where(Department.id == department_id))
    obj = obj_exp.scalars().one_or_none()

    if not obj:
        raise DepartmentNotFoundException()

    return obj
