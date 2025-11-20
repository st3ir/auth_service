from typing import Annotated, Sequence

from fastapi import Depends
from sqlalchemy import Select, select
from sqlalchemy.engine.row import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from api.users.schemas import UserTTInfo
from db.session import get_db
from service.auth.handlers import get_active_user_from_cookie
from service.exceptions.api.rights import (
    InsufficientRightsException,
    RightsNotFoundException,
)
from service.helpers.group_by import group_rows_by_field
from service.rights.models import SpecRights, UserRights
from service.rights.types import RightScoreType, RightType, SourceType
from service.roles.types import RoleType
from service.users.models import User


async def get_sources_by_user_id(
    source_type: SourceType,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, list[int]]:

    query = get_share_rights_query(
        [UserRights.subject_id == user_id, SpecRights.source_type == source_type],
        [SpecRights.right_type],
    )

    rights = (await db.execute(query)).mappings().all()
    grouped_rights = await group_rows_by_field(rights, 'right_type')

    source_ids_by_right_scope = {
        'assigned_source_ids': [
            right['source_id']
            for right
            in rights
        ],
        'grouped': {
            right_type: [r['source_id'] for r in rights_seq]
            for right_type, rights_seq
            in grouped_rights.items()
        }
    }

    return source_ids_by_right_scope


async def get_user_right_by_right_id(
    user_ids: list[int],
    right_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SpecRights | None:

    return (
        await db.execute(
            select(UserRights)
            .where(
                UserRights.subject_id.in_(user_ids),
                UserRights.right_id == right_id,
            )
        )
    ).scalars().one_or_none()


async def get_rights_by_type(
    source_type: SourceType,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Sequence[RowMapping]:

    return (
        await db.execute(
            get_share_rights_query([SpecRights.source_type == source_type])
        )
    ).mappings().all()


async def get_right_by_user_id(
    db: AsyncSession,
    subject_id: int,
    source_id: int,
) -> UserRights | None:

    return (
        await db.execute(
            select(UserRights)
            .join(SpecRights)
            .where(
                SpecRights.source_id == source_id,
                UserRights.subject_id == subject_id
            )
        )
    ).scalars().one_or_none()


async def get_highest_user_right(
    user_rights: Sequence[SpecRights | RowMapping],
) -> SpecRights:

    return max(user_rights, key=lambda right: RightScoreType[right.right_type])


async def get_spec_right_by_user_id(
    db: Annotated[AsyncSession, Depends(get_db)],
    subject_id: int,
    source_id: int,
    source_type: SourceType
) -> RowMapping | None:

    rights = (
        await db.execute(
            get_share_rights_query(
                [
                    SpecRights.source_id == source_id,
                    SpecRights.source_type == source_type,
                    UserRights.subject_id == subject_id
                ]
            )
        )
    ).mappings().all()

    if not rights:
        raise RightsNotFoundException()

    return await get_highest_user_right(rights)


async def get_right_by_rel_id(
    source_id: int,
    user: Annotated[UserTTInfo, Depends(get_active_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UserRights | None:

    right = await get_right_by_user_id(db, user.id, source_id)
    if not right:
        raise RightsNotFoundException()

    return right


async def get_granted_users_by_rel_id(
    source_id: int,
    source_type: SourceType,
    user: Annotated[UserTTInfo, Depends(get_active_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    right_type: RightType | None = None
) -> dict[str, list]:

    query = get_share_rights_query(
        [
            SpecRights.source_type == source_type,
            SpecRights.source_id == source_id,
        ],
        [SpecRights.right_type],
    )
    query = query.add_columns(
        User.first_name, User.last_name,
        User.parent_name, User.photo_link
    )
    query = query.join(User, UserRights.subject_id == User.id)

    if right_type:
        query = query.where(SpecRights.right_type == right_type)

    return await group_rows_by_field(
        (await db.execute(query)).mappings().all(), 'right_type'
    )


async def user_can_grant_rights_to_obj(
    db: AsyncSession,
    user: UserTTInfo,
    source_id: int,
    source_type: SourceType,
    by_nested: bool = False
) -> bool:

    if user.role in [
        RoleType.USER_MASTER, RoleType.SERVICE_USER, RoleType.HR_DIRECTOR
    ]:
        return True

    if by_nested:
        return True

    right = await get_spec_right_by_user_id(db, user.id, source_id, source_type)
    if (
        not right
        or (right and right.right_type != RightType.MANAGE)
    ):
        raise InsufficientRightsException()

    return True


def get_share_rights_query(
    where_conds: list | None = None,
    order_by: list | None = None
):

    query = (
        select(
            SpecRights.id.label("spec_right_id"),
            SpecRights.right_type,
            SpecRights.source_id,
            SpecRights.source_type,
            UserRights.id.label("user_right_id"),
            UserRights.right_id,
            UserRights.subject_id,
            UserRights.constraints,
        )
        .select_from(SpecRights)
        .join(UserRights, SpecRights.id == UserRights.right_id)
    )

    if where_conds:
        query = query.where(*where_conds)

    if order_by:
        query = query.order_by(*order_by)

    return query
