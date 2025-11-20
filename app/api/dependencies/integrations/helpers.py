import logging

from sqlalchemy import case, delete, exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from api.users.integrations.schemas import (
    AppUserCredentials,
    BaseIntegrationUserStateSchema,
)
from db.utils.transactional import transaction
from service.exceptions.api.integrations import (
    UserAppCredentialsNotFoundException,
)
from service.exceptions.api.users import UserNotFoundException
from service.organizations.models import Department, Organization, JobSitePolicy
from service.rights.models import SpecRights, UserRights
from service.rights.types import RightType, SourceType
from service.types import IntegrationUserState, JobSiteMacroEnum
from service.users.models import JobSiteCredentials, User

logger = logging.getLogger(__name__)


async def get_app_user_credentials(
    db: AsyncSession,
    user_id: int,
    platform_type: JobSiteMacroEnum
) -> JobSiteCredentials | None:

    query = (
        select(JobSiteCredentials)
        .where(
            JobSiteCredentials.user_id == user_id,
            JobSiteCredentials.platform_type == platform_type,
        )
    )

    return (await db.execute(query)).scalar()


async def get_organization_job_site_policy(
    db: AsyncSession,
    organization_id: int,
    platform_type: JobSiteMacroEnum
) -> JobSitePolicy | None:

    return (
        await db.execute(
            select(JobSitePolicy)
            .where(
                JobSitePolicy.organization_id == organization_id,
                JobSitePolicy.platform_type == platform_type,
            )
        )
    ).scalar()


async def update_app_user_credentials(
    db: AsyncSession,
    user_id: int,
    platform_type: JobSiteMacroEnum,
    creds: AppUserCredentials
) -> JobSiteCredentials:

    query = (
        exists(User.id)
        .select()
        .where(User.id == user_id)
    )
    q_res = (await db.execute(query)).scalar()

    if not q_res:
        raise UserNotFoundException()

    db_creds = await get_app_user_credentials(db, user_id, platform_type)

    u_creds = creds.credentials.model_dump()
    u_creds["updated_at"] = str(u_creds["updated_at"])
    u_creds["created_at"] = str(u_creds["created_at"])

    async with transaction(db):
        if not db_creds:
            db_creds = JobSiteCredentials(
                user_id=user_id,
                credentials=u_creds,
                platform_type=platform_type,
            )
        else:
            db_creds.credentials = u_creds

        db.add(db_creds)

    await db.refresh(db_creds)

    return db_creds


async def get_users_with_credentials(
    db: AsyncSession,
    user_id: int,
    vacancy_id: int
) -> list:

    rights_on_vacancy_subq = (
        select(SpecRights.right_type, UserRights.subject_id)
        .join(
            UserRights,
            UserRights.right_id == SpecRights.id
        )
        .where(
            SpecRights.source_id == vacancy_id,
            SpecRights.source_type == SourceType.VACANCY,
            SpecRights.right_type == RightType.MANAGE
        )
        .subquery()
    )

    org_subq = (
        select(Organization.id)
        .select_from(User)
        .where(User.id == user_id)
        .join(
            Department,
            Department.id == User.department_id
        )
        .join(
            Organization,
            Organization.id == Department.organization_id
        )
        .subquery()
    )

    deps_sub_q = (
        select(Department.id)
        .where(Department.organization_id == org_subq.c.id)
        .subquery()
    )

    users_q = (
        select(
            User.id.label("user_id"),
            case(
                (rights_on_vacancy_subq.c.subject_id.is_(None), False),
                else_=True
            ).label("is_priority")
        )
        .outerjoin(
            rights_on_vacancy_subq,
            rights_on_vacancy_subq.c.subject_id == User.id
        )
        .join(
            JobSiteCredentials,
            JobSiteCredentials.user_id == User.id
        )
        .where(
            User.department_id.in_(select(deps_sub_q.c.id)),
            JobSiteCredentials.credentials != {}
        )
        .distinct(User.id)
    )

    return (await db.execute(users_q)).mappings().all()


async def get_integration_users_states(
    db: AsyncSession,
    user: User
) -> list[dict]:

    good_states = [IntegrationUserState.OK]

    query = (
        select(
            JobSiteCredentials.credentials.op("->")("user_state").label("user_state"),
            JobSiteCredentials.platform_type,
            case(
                (
                    JobSiteCredentials.credentials
                    .op("->")("user_state")
                    .op("->")("state")
                    .in_(good_states), True
                ), else_=False
            ).label('is_success')
        )
        .where(JobSiteCredentials.user_id == user.id)
    )

    result = (await db.execute(query)).mappings().all()

    return {
        e["platform_type"]: {
            "state": e["user_state"]["state"],
            "reason": e["user_state"]["reason"],
            "is_success": e["is_success"],
        }
        for e in result
    }


async def update_integration_user_state(
    db: AsyncSession,
    user_id: int,
    platform_type: JobSiteMacroEnum,
    usr_state: BaseIntegrationUserStateSchema,
) -> None:

    query = (
        select(JobSiteCredentials)
        .where(
            JobSiteCredentials.user_id == user_id,
            JobSiteCredentials.platform_type == platform_type
        )
    )

    db_creds = (await db.execute(query)).scalar()
    if not db_creds:
        raise UserAppCredentialsNotFoundException

    if not db_creds.credentials.get("user_state"):
        raise UserAppCredentialsNotFoundException

    async with transaction(db):
        db_creds.credentials["user_state"] = usr_state.model_dump()

        flag_modified(db_creds, "credentials")
        db.add(db_creds)


async def unlink_job_site_by_user(
    db: AsyncSession,
    user: User,
    platform_type: JobSiteMacroEnum
) -> None:

    async with transaction(db):
        await db.execute(
            delete(JobSiteCredentials)
            .where(
                JobSiteCredentials.platform_type == platform_type,
                JobSiteCredentials.user_id == user.id
            )
        )
