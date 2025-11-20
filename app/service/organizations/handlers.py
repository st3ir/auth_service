from sqlalchemy import func, insert, select, update, Select
from sqlalchemy.ext.asyncio import AsyncSession

from db.utils.transactional import transaction
from service.helpers.group_by import group_rows_by_field
from service.organizations.models import Department, Organization
from service.types import JobSiteMacroEnum


def get_departments_by_condition_query(
    where_conditions: list,
    fields: list | None = None,
    join_conditions: list[tuple] | None = None,
) -> Select[Department]:

    select_stmt = select(*fields) if fields else select(Department)

    if join_conditions:
        for join_condition in join_conditions:
            select_stmt = select_stmt.join(*join_condition)

    return select_stmt.where(*where_conditions)


async def get_departments_by_org_with_external_id(
    db: AsyncSession,
    organization_id: int,
    integration_type: JobSiteMacroEnum,
) -> dict[str, int]:

    departments = (
        await db.execute(
            get_departments_by_condition_query(
                fields=[Department.id, Department.external_id],
                where_conditions=[
                    Department.organization_id == organization_id,
                    Department.external_type == integration_type,
                    Department.external_id.isnot(None),
                ]
            )
        )
    ).mappings().all()

    return {x.external_id: x.id for x in departments}


async def get_departments_by_organizations(
    db: AsyncSession,
    organization_ids: list[int],
    department_name: str
) -> list[Department]:

    obj = (
        await db.execute(
            select(
                Department.id,
                Department.full_name,
                Organization.full_name.label("organization_name")
            )
            .join(Organization, Department.organization_id == Organization.id)
            .where(
                Department.organization_id.in_(organization_ids),
                func.lower(Department.full_name).ilike('%{}%'.format(department_name))
            )
            .order_by(Organization.id)
        )
    ).mappings().all()

    return await group_rows_by_field(obj, "organization_name")


