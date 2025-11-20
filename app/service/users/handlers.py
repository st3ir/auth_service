from uuid import uuid4

from sqlalchemy import Boolean, Select, case, cast, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.users import schemas
from api.users.schemas import User as UserSchema
from api.users.schemas import UserCreate, UserFullInfo, UserTTInfo
from db.utils.transactional import transaction
from service.exceptions.api.users import (
    UserEmailAlreadyExistsException,
    UserNotFoundException,
)
from service.helpers import utils
from service.organizations.models import Department, Organization
from service.rights.models import SpecRights, UserRights
from service.rights.types import SourceType
from service.roles.handlers import get_default_user_role
from service.roles.models import Role, UserRole
from service.roles.types import RoleType
from service.users.models import User


async def create_user(
    db: AsyncSession, user: UserCreate,
    role: Role | None, img: str | None
) -> UserSchema:

    user_exists = (
        await db.execute(select(User).where(User.email == user.email))
    ).unique().all()

    if user_exists:
        e = UserEmailAlreadyExistsException()
        e.exc_info = e.exc_info.format(user.email)
        raise e

    pass_salt = uuid4().hex

    async with transaction(db):
        new_user = User(
            pass_salt=pass_salt,
            password=utils.get_hash(user.password + pass_salt),
            email=user.email,
            photo_link=img,
            active=user.active,
            first_name=user.first_name,
            last_name=user.last_name,
            parent_name=user.parent_name,
            department_id=user.department_id
        )

        if not role:
            role = await get_default_user_role(db)
        new_user.roles.append(role)

        db.add(new_user)

    await db.refresh(new_user)
    return new_user


async def update_user(
    db: AsyncSession,
    user_id: int,
    new_user: schemas.UserUpdateSchema,
    role: Role,
    img: str | None
) -> dict:

    old_user = (
        await db.execute(select(User).filter(User.id == user_id))
    ).scalars().one_or_none()

    if not old_user:
        raise UserNotFoundException()

    if img:
        old_user.photo_link = img

    new_data = new_user.model_dump(exclude_none=True)

    for key, value in new_data.items():
        setattr(old_user, key, value)

    if role not in old_user.roles:
        old_user.roles.append(role)

    async with transaction(db):
        db.add(old_user)

    await db.refresh(old_user)
    return old_user


async def get_users_by_roles(
    db: AsyncSession,
    organization_id: int,
    roles: list[RoleType],
    source_id: int | None = None,
    source_type: SourceType | None = None
) -> list[UserTTInfo]:

    users_query = get_share_user_query(
        [
            Role.rolename.in_(roles),
            Department.organization_id == organization_id
        ]
    )

    if source_id and source_type:
        user_rights_subquery = (
            select(UserRights.subject_id)
            .distinct(UserRights.subject_id)
            .join(SpecRights, UserRights.right_id == SpecRights.id)
            .where(
                SpecRights.source_id == source_id,
                SpecRights.source_type == source_type
            )
            .subquery()
        )

        users_query = (
            users_query
            .add_columns(
                case(
                    (cast(user_rights_subquery.c.subject_id, Boolean).is_(True), True),
                    else_=False
                ).label('is_assigned')
            )
            .outerjoin(
                user_rights_subquery, User.id == user_rights_subquery.c.subject_id
            )
        )

    return (await db.execute(users_query)).mappings().all()


async def get_users(
    db: AsyncSession,
    user_ids: list[int]
) -> list[UserFullInfo]:

    return (
        await db.execute(get_share_user_query([User.id.in_(user_ids)]))
    ).mappings().all()


async def get_organization_by_user_id(
    db: AsyncSession,
    user_id: int,
) -> int | None:

    return (
        await db.execute(
            select(Department.organization_id)
            .join(User, User.department_id == Department.id)
            .where(User.id == user_id)
        )
    ).scalar()


def get_share_user_query(
    where_conds: list | None = None,
) -> Select:

    query = (
        select(
            User.id,
            User.first_name,
            User.last_name,
            User.photo_link,
            User.email,
            User.department_id,
            Role.rolename.label('role'),
            Organization.corp_phone,
            Organization.full_name.label('organization_name'),
        )
        .select_from(User)
        .join(UserRole, UserRole.user_id == User.id)
        .join(Role, Role.id == UserRole.role_id)
        .join(Department, Department.id == User.department_id)
        .join(Organization, Organization.id == Department.organization_id)
        .where(*where_conds)
    )

    return query


async def get_dir_by_organization(
    db: AsyncSession,
    organization_id: int,
) -> dict:

    return (
        await db.execute(
            get_share_user_query([
                Role.rolename == RoleType.HR_DIRECTOR,
                Organization.id == organization_id
            ])
            .add_columns(
                User.active,
                User.is_internal,
                Organization.id.label('organization_id')
            )
        )
    ).mappings().first()
