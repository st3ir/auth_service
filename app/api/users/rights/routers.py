from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.rights.helpers import (
    get_granted_users_by_rel_id,
    get_right_by_user_id,
    get_rights_by_type,
    get_sources_by_user_id,
    get_spec_right_by_user_id,
    user_can_grant_rights_to_obj,
)
from api.users.rights.schemas import (
    GrantedSourcesSchema,
    GrantRightSchema,
    GrantRightToUsersSchema,
    GroupedUsersWithGrantsSchema,
    RightsChangedSchema,
    RightSchema,
    RightSchemaBase,
)
from api.users.schemas import UserTTInfo
from db.session import get_db
from db.utils.transactional import transaction
from service.auth.handlers import get_active_user_from_cookie
from service.exceptions.api.rights import RightsNotFoundException
from service.rights.handlers import (
    change_rights_to_users_by_rel_id,
    check_right_with_role_cond,
    update_right_of_user,
)
from service.rights.models import SpecRights, UserRights

api_router = APIRouter(prefix='/rights')


@api_router.get("", response_model=list[RightSchema], status_code=status.HTTP_200_OK)
async def get_rights_by_source_type(
    rights_by_type: Annotated[dict, Depends(get_rights_by_type)],
    user: Annotated[UserTTInfo, Depends(get_active_user_from_cookie)]
):

    return rights_by_type


@api_router.get(
    "/by-rel/{source_id}",
    response_model=GroupedUsersWithGrantsSchema,
    status_code=status.HTTP_200_OK
)
async def get_granted_users_by_source_id(
    users_by_rel: Annotated[UserRights, Depends(get_granted_users_by_rel_id)]
):

    return users_by_rel


@api_router.put(
    "/by-rel/{source_id}",
    response_model=RightsChangedSchema,
    status_code=status.HTTP_200_OK
)
async def set_rights_to_users(
    source_id: int,
    users_for_grant: GrantRightToUsersSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserTTInfo, Depends(get_active_user_from_cookie)],
    by_nested: bool = False
):

    await user_can_grant_rights_to_obj(
        db,
        user,
        source_id,
        users_for_grant.source_type,
        by_nested
    )

    await check_right_with_role_cond(
        db, users_for_grant.right_type, users_for_grant.user_ids_in
    )

    await change_rights_to_users_by_rel_id(
        db, users_for_grant, source_id
    )

    return {
        'is_changed': True
    }


@api_router.get(
    '/by-rel/{source_id}/{subject_id}',
    response_model=RightSchemaBase,
    status_code=status.HTTP_200_OK
)
async def get_user_highest_right_by_source_id(
    spec_right_by_rel: Annotated[RowMapping, Depends(get_spec_right_by_user_id)],
    user: Annotated[UserTTInfo, Depends(get_active_user_from_cookie)],
):

    return spec_right_by_rel


@api_router.put(
    "/by-rel/{source_id}/{subject_id}",
    response_model=RightSchemaBase,
    status_code=status.HTTP_200_OK,
)
async def update_right_to_user_by_source_id(
    source_id: int,
    grant_schema: GrantRightSchema,
    spec_right_by_rel: Annotated[RowMapping, Depends(get_spec_right_by_user_id)],
    user: Annotated[UserTTInfo, Depends(get_active_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    by_nested: bool = False
):

    await user_can_grant_rights_to_obj(
        db,
        user,
        source_id,
        grant_schema.source_type,
        by_nested
    )

    right = await update_right_of_user(db, spec_right_by_rel, grant_schema, source_id)

    return RightSchemaBase(
        **right.__dict__,
        constraints=spec_right_by_rel.constraints
    )


@api_router.delete(
    "/by-rel/{source_id}/{subject_id}",
    status_code=status.HTTP_200_OK
)
async def delete_right_by_source_id(
    source_id: int,
    subject_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):

    right = await get_right_by_user_id(db, subject_id, source_id)
    if not right:
        raise RightsNotFoundException()

    async with transaction(db):
        await db.delete(right)

    return right


@api_router.get(
    "/by-user/{user_id}",
    response_model=GrantedSourcesSchema,
    status_code=status.HTTP_200_OK
)
async def get_user_rights_by_source_id(
    user_rights: Annotated[dict, Depends(get_sources_by_user_id)]
):

    return user_rights
