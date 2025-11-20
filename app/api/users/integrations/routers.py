from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.integrations.helpers import (
    get_app_user_credentials,
    get_integration_users_states,
    get_organization_job_site_policy,
    get_users_with_credentials,
    unlink_job_site_by_user,
    update_app_user_credentials,
    update_integration_user_state,
)
from api.dependencies.integrations.types import JOB_SITE_MICRO_MAP
from api.users.integrations.schemas import (
    AppUserCredentials,
    BaseIntegrationUserStateSchema,
    ServiceUserJobSitePolicy,
    UserIntegrationStatesSchema,
    UsersWithCredsSchema,
)
from db.session import get_db
from service.auth.handlers import (
    get_active_user_from_cookie,
    get_active_user_from_header,
)
from service.exceptions.api.integrations import (
    UserAppCredentialsNotFoundException,
    JobSitePolicyNotFoundException,
)
from service.types import JobSiteMicroEnum
from service.users.handlers import get_organization_by_user_id
from service.users.models import User

api_router = APIRouter(prefix="/integrations")


@api_router.get(
    path="/users/with-creds",
    response_model=UsersWithCredsSchema,
    status_code=status.HTTP_200_OK
)
async def users_with_credentials(
    user: Annotated[User, Depends(get_active_user_from_header)],
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int,
    vacancy_id: int,
):

    return await get_users_with_credentials(db, user_id, vacancy_id)


@api_router.get(
    path="/users/states",
    response_model=UserIntegrationStatesSchema,
    status_code=status.HTTP_200_OK
)
async def integration_users_states(
    user: Annotated[User, Depends(get_active_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
):

    return await get_integration_users_states(db, user)


@api_router.delete(
    "/{platform_type}/unlink"
)
async def unlink_job_site(
    user: Annotated[User, Depends(get_active_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    platform_type: JobSiteMicroEnum,
):

    await unlink_job_site_by_user(db, user, platform_type.upper())

    return {"is_changed": True}


@api_router.get(
    path="/{platform_type}/{user_id}",
    response_model=AppUserCredentials,
    status_code=status.HTTP_200_OK
)
async def get_credentials(
    user: Annotated[User, Depends(get_active_user_from_header)],
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int,
    platform_type: JobSiteMicroEnum,
):

    result = await get_app_user_credentials(
        db, user_id, JOB_SITE_MICRO_MAP[platform_type]
    )
    if not result:
        raise UserAppCredentialsNotFoundException()

    return {
        "id": result.id,
        "user_id": result.user_id,
        "platform_type": JOB_SITE_MICRO_MAP[platform_type],
        "credentials": result.credentials,
    }


@api_router.get(
    path="/policy/{platform_type}/{user_id}",
    response_model=ServiceUserJobSitePolicy,
    status_code=status.HTTP_200_OK
)
async def get_organization_policy(
    user: Annotated[User, Depends(get_active_user_from_header)],
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int,
    platform_type: JobSiteMicroEnum,
):
    organization_id = await get_organization_by_user_id(db, user_id)
    result = await get_organization_job_site_policy(
        db, organization_id, JOB_SITE_MICRO_MAP[platform_type]
    )
    if not result:
        raise JobSitePolicyNotFoundException()

    return {
        "organization_id": result.organization_id,
        "platform_type": JOB_SITE_MICRO_MAP[platform_type],
        "billing_type": result.billing_info,
    }


@api_router.put(
    path="/{platform_type}/{user_id}",
    response_model=AppUserCredentials,
    status_code=status.HTTP_200_OK
)
async def create_or_update_credentials(
    user: Annotated[User, Depends(get_active_user_from_header)],
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int,
    platform_type: JobSiteMicroEnum,
    creds: AppUserCredentials,
):

    result = await update_app_user_credentials(
        db, user_id, JOB_SITE_MICRO_MAP[platform_type], creds
    )

    return {
        "user_id": result.user_id,
        "platform_type": JOB_SITE_MICRO_MAP[platform_type],
        "credentials": result.credentials,
    }


@api_router.put(
    path="/{platform_type}/{user_id}/state",
    response_model=None,
    status_code=status.HTTP_200_OK
)
async def integration_user_state(
    user: Annotated[User, Depends(get_active_user_from_header)],
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int,
    platform_type: JobSiteMicroEnum,
    usr_state: BaseIntegrationUserStateSchema,
):

    await update_integration_user_state(
        db,
        user_id,
        JOB_SITE_MICRO_MAP[platform_type],
        usr_state,
    )
