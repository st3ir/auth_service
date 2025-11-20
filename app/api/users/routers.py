from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.users.schemas import (
    UserCreate,
    UserFullInfo,
    UserInfoWithAssign,
    UserTTInfo,
    UserTTInfoPhone,
    UserUpdateSchema,
    UserVerifyInfo,
)
from db.session import get_db
from service.auth import handlers as auth_handlers
from service.exceptions.api.users.exc import EulaMustBeAcceptedException
from service.rights.types import SourceType
from service.roles.handlers import check_user_role_existence
from service.roles.models import Role
from service.roles.types import RoleType
from service.users import handlers as user_handlers
from service.users.media.handlers import process_image
from service.users.media.helpers import get_user_image_name
from settings import auth_settings as a_s

api_router = APIRouter(prefix="/users")


@api_router.post(
    "",
    response_model=UserTTInfo,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    user: Annotated[
        UserTTInfo,
        Depends(auth_handlers.get_active_user_from_cookie)
    ],
    role: Annotated[
        Role,
        Depends(check_user_role_existence)
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
    user_schema: UserCreate = Depends(UserCreate.as_form),
    img: UploadFile = File(None),
):
    if img:
        img = await process_image(img)

    return await user_handlers.create_user(db, user_schema, role, img)


@api_router.get("/by-ids", response_model=list[UserFullInfo])
async def get_users_by_ids(
    user: Annotated[
        UserTTInfo,
        Depends(auth_handlers.get_active_user_from_cookie)
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
    user_ids: list[int] = Query(),
):

    return await user_handlers.get_users(db, user_ids)


@api_router.put(
    "/{user_id}",
    response_model=UserTTInfo,
    status_code=status.HTTP_201_CREATED
)
async def update_user(
    user_id: int,
    user: Annotated[
        UserTTInfo,
        Depends(auth_handlers.get_active_user_from_cookie)
    ],
    role: Annotated[
        Role | None,
        Depends(check_user_role_existence)
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
    updated_info: UserUpdateSchema = Depends(
        UserUpdateSchema.as_form
    ),
    img: UploadFile = File(None),
):
    if img:
        oldest_img = await get_user_image_name(db, user_id)
        img = await process_image(img, oldest_img)

    return await user_handlers.update_user(
        db, user_id, updated_info, role, img
    )


@api_router.get(
    "/whoami",
    response_model=UserTTInfoPhone,
    status_code=status.HTTP_200_OK
)
async def get_info_of_me(
    user: Annotated[
        UserTTInfoPhone,
        Depends(auth_handlers.get_active_user_from_cookie)
    ],
):
    if bool(int(a_s.SKIP_AUTH)):
        return {
            'id': 1,
            'email': 'test@test.com',
            "phone_number": "+1234567890",
            'first_name': 'test name',
            'last_name': 'test last_name',
            'parent_name': 'test parent_name',
            'role': 'HR_RECRUITER',

            'department_id': 1,
            'organization_id': 1,
            'is_internal': True
        }

    return user


@api_router.get(
    "/verify",
    status_code=status.HTTP_200_OK
)
async def verify(
    user: Annotated[
        UserTTInfo,
        Depends(auth_handlers.get_active_user_from_header)
    ],
):

    if not bool(a_s.SKIP_AGREEMENT):
        if (
            user.role != RoleType.SERVICE_USER
            and not user.is_eula_accepted
        ):
            raise EulaMustBeAcceptedException

    return UserVerifyInfo(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        parent_name=user.parent_name,
        photo_link=user.photo_link,
        role=user.role,
        department_id=user.department_id,
        organization_id=user.organization_id,
    )


@api_router.get("/by-roles", response_model=list[UserInfoWithAssign])
async def get_users_by_roles(
    user: Annotated[
        UserTTInfo,
        Depends(auth_handlers.get_active_user_from_cookie)
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
    organization_id: int | None = None,
    roles: list[RoleType] = Query(default_factory=list),
    source_id: int | None = None,
    source_type: SourceType = Query(None),
):

    return await user_handlers.get_users_by_roles(
        db, organization_id or user.organization_id, roles, source_id, source_type
    )


@api_router.get("/dir-by-org", response_model=UserTTInfo)
async def get_dir_by_org(
    user: Annotated[
        UserTTInfo,
        Depends(auth_handlers.get_active_user_from_cookie)
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
    organization_id: int | None = None
):

    return await user_handlers.get_dir_by_organization(
        db, organization_id
    )
