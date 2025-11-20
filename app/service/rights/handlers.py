from sqlalchemy import RowMapping, delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.users.rights.schemas import (
    ConstraintsSchema,
    GrantRightSchema,
    GrantRightToUsersSchema,
)
from db.utils.transactional import transaction
from service.exceptions.api.users import RightNotMatchWithUserRole
from service.rights.models import SpecRights, UserRights
from service.rights.types import ROLE_TO_RIGHTS_MAP, RightType, SourceType
from service.users.models import User


async def get_or_create_right(
    db: AsyncSession,
    source_id: int,
    source_type: SourceType,
    right_type: RightType
) -> SpecRights:

    right = (
        await db.execute(
            select(SpecRights)
            .where(
                SpecRights.source_id == source_id,
                SpecRights.source_type == source_type,
                SpecRights.right_type == right_type,
            )
        )
    ).scalar_one_or_none()

    if not right:
        async with transaction(db):
            right = SpecRights(
                source_type=source_type,
                source_id=source_id,
                right_type=right_type
            )
            db.add(right)
        await db.refresh(right)

    return right


async def add_right_to_users(
    db: AsyncSession,
    user_ids: list[int],
    constraints: ConstraintsSchema,
    spec_right: SpecRights,
) -> None:

    db_users_rights = (
        await db.execute(
            select(UserRights)
            .join(
                SpecRights,
                SpecRights.id == UserRights.right_id
            )
            .where(
                UserRights.subject_id.in_(user_ids),
                SpecRights.source_type == spec_right.source_type,
                SpecRights.source_id == spec_right.source_id
            )
        )
    ).scalars().all()

    create_lst = []
    update_users_ids = []
    db_user_ids = [e.subject_id for e in db_users_rights]
    for user_id in user_ids:
        dct = {
            "subject_id": user_id,
            "right_id": spec_right.id,
            "constraints": constraints.model_dump(exclude_none=True)
        }

        if user_id not in db_user_ids:
            create_lst.append(dct)
        else:
            update_users_ids.append(user_id)

    async with transaction(db):
        if create_lst:
            await db.execute(insert(UserRights.__table__), create_lst)

        for user_right in db_users_rights:
            if user_right.subject_id in update_users_ids:
                user_right.right_id = spec_right.id
                user_right.constraints = constraints.model_dump(exclude_none=True)


async def revoke_right_of_users(
    db: AsyncSession,
    user_ids: list[int],
    right_id: int
) -> None:

    async with transaction(db):
        u_right_table = UserRights.__table__
        await db.execute(
            delete(u_right_table)
            .where(
                u_right_table.c.right_id == right_id,
                u_right_table.c.subject_id.in_(user_ids)
            )
        )


async def change_rights_to_users_by_rel_id(
    db: AsyncSession,
    right_schema: GrantRightToUsersSchema,
    source_id: int
) -> UserRights:

    right = await get_or_create_right(
        db, source_id, right_schema.source_type, right_schema.right_type
    )
    if right_schema.user_ids_in:

        await add_right_to_users(
            db,
            right_schema.user_ids_in,
            right_schema.constraints,
            right
        )

    if right_schema.user_ids_out:
        await revoke_right_of_users(db, right_schema.user_ids_out, right.id)


async def update_right_of_user(
    db: AsyncSession,
    right: RowMapping,
    right_schema: GrantRightSchema,
    source_id: int
) -> SpecRights:

    values = {
        'source_id': source_id,
        'source_type': right_schema.source_type,
        'right_type': right_schema.right_type,
    }
    async with transaction(db):
        return (
            await db.execute(
                update(SpecRights)
                .where(SpecRights.id == right.spec_right_id)
                .values(**values)
                .returning(SpecRights)
            )
        ).scalar()


async def check_right_with_role_cond(
    db: AsyncSession,
    right_type: RightType,
    users_ids_in: list[int],
) -> None:

    users_res = (
        await db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.id.in_(users_ids_in))
        )
    ).scalars().all()

    for user in users_res:
        if right_type not in ROLE_TO_RIGHTS_MAP[user.role.rolename]:
            txt = RightNotMatchWithUserRole.exc_info
            raise RightNotMatchWithUserRole(exc_info=txt.format(user.id))
