from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.organizations.helpers import get_department_if_exist
from api.organizations.schemas import (
    DetailDepartmentSchema,
    DepartmentWithOrgSchema,
    DepartmentWithExternalSchema
)
from db.session import get_db
from service.auth.handlers import get_active_user_from_cookie
from service.organizations.handlers import (
    get_departments_by_organizations,
    get_departments_by_org_with_external_id
)
from service.types import JobSiteMacroEnum
from service.users.models import User

api_router = APIRouter(prefix="/organizations")


@api_router.get("/departments", response_model=DepartmentWithOrgSchema)
async def get_departments(
    user: Annotated[User, Depends(get_active_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    organization_ids: list[int] = Query(None),
    department_name: str = ''
):

    return await get_departments_by_organizations(db, organization_ids, department_name)


@api_router.get(
    "/departments/with-external",
    response_model=DepartmentWithExternalSchema
)
async def get_departments_with_external_id(
    user: Annotated[User, Depends(get_active_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    organization_id: int,
    integration_type: JobSiteMacroEnum = JobSiteMacroEnum.HUNTFLOW
):

    return await get_departments_by_org_with_external_id(
        db, organization_id, integration_type
    )


@api_router.get("/departments/{department_id}", response_model=DetailDepartmentSchema)
async def get_department(
    department: Annotated[DetailDepartmentSchema, Depends(get_department_if_exist)],
    user: Annotated[User, Depends(get_active_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
):

    return department
