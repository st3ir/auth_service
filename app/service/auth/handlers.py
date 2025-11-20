from typing import Annotated

import redis.asyncio as aioredis
from fastapi import Cookie, Depends, Header, Request, Response, status
from jose import ExpiredSignatureError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.users.schemas import UserTTInfo
from db.session import get_db
from service.auth import types
from service.exceptions.api.users import (
    ExpiredUserTokenException,
    InactiveUserException,
    InvalidLoginDataException,
    InvalidUserRoleException,
    InvalidUserTokenException,
    UserNotFoundException,
)
from service.helpers import utils
from service.helpers.url_utils import extract_base_url
from service.organizations.models import Department
from service.roles.handlers import check_user_role_existence
from service.roles.models import Role, UserRole
from service.roles.types import RoleType
from service.types import UserAgreementType
from service.users.models import User, UserAgreement
from settings import auth_settings as a_s
from settings import redis_settings as r_s

redis = aioredis.from_url(r_s.REDIS_URL, decode_responses=True)


async def create_tokens_pair(
    user: UserTTInfo | User,
    user_role: RoleType,
    user_agent: str | None = None
) -> tuple[types.AccessToken, types.RefreshToken]:

    access_token = utils.create_token(
        data={
            "email": user.email,
            "user_id": user.id,
            "role": user_role,
            "device_id": utils.encode_to_base64(user_agent)
        },
        minutes=int(a_s.ACCESS_TOKEN_EXPIRES_MINUTES),
        secret_key=a_s.ACCESS_TOKEN_SECRET_KEY,
        algorithm=a_s.TOKENS_ALGORITHM,
    )
    refresh_token = utils.create_token(
        data={"email": user.email},
        minutes=int(a_s.REFRESH_TOKEN_EXPIRES_MINUTES),
        secret_key=a_s.REFRESH_TOKEN_SECRET_KEY,
        algorithm=a_s.TOKENS_ALGORITHM,
    )

    await redis.set(
        access_token,
        refresh_token,
        int(a_s.REFRESH_TOKEN_EXPIRES_MINUTES) * 60
    )
    return access_token, refresh_token


async def get_user_by_email(
    db: AsyncSession,
    email: str
) -> User | None:

    return (await db.execute(select(User).where(User.email == email))).scalar()


async def get_user_info(
    db: AsyncSession,
    email: str
) -> UserTTInfo:
    organization_id_sub_query = select(
        Department.id, Department.organization_id
    ).select_from(Department).subquery()

    role_name_sub_query = select(
        UserRole.user_id, Role.rolename
    ).join(
        Role, UserRole.role_id == Role.id
    ).subquery()

    fields = [
        User.id,
        User.active,
        User.email,
        User.first_name,
        User.department_id,
        User.photo_link,
        User.last_name,
        User.parent_name,
        User.phone_number,
        User.is_internal,
        organization_id_sub_query.c.organization_id,
        role_name_sub_query.c.rolename.label("role")
    ]

    query = (
        select(*fields)
        .where(User.email == email)
        .outerjoin(
            organization_id_sub_query,
            User.department_id == organization_id_sub_query.c.id
        ).outerjoin(
            role_name_sub_query,
            User.id == role_name_sub_query.c.user_id
        ).group_by(*fields)
    )

    user = (await db.execute(query)).mappings().one_or_none()

    if not user:
        raise UserNotFoundException()

    if not bool(a_s.SKIP_AGREEMENT):
        agreements_query = (
            select(UserAgreement.agreement_type)
            .where(
                UserAgreement.user_id == user.id,
                UserAgreement.organization_id == user.organization_id
            )
        )
        agreements = await db.execute(agreements_query)
        agreements = agreements.scalars().all()
        is_eula_accepted = UserAgreementType.EULA in agreements
    else:
        is_eula_accepted = True

    return UserTTInfo(
        **user,
        is_eula_accepted=is_eula_accepted
    )


async def decode_token(
    token: str,
    secret_key: str,
) -> dict | None:
    try:
        return jwt.decode(
            token,
            secret_key,
            algorithms=[a_s.TOKENS_ALGORITHM]
        )
    except ExpiredSignatureError:
        return None
    except Exception:
        raise InvalidUserTokenException()


async def get_user_from_token(
    db: AsyncSession,
    request: Request,
    response: Response,
    access_token: types.AccessToken
) -> UserTTInfo:

    token: types.AccessTokenTD = await decode_token(
        access_token, a_s.ACCESS_TOKEN_SECRET_KEY
    )

    origin = extract_base_url(request.headers.get('origin'))
    referer = extract_base_url(request.headers.get('referer'))
    host = extract_base_url(request.headers.get('host'))

    domain = f'{origin or referer or host or a_s.DOMAIN_URL}'

    if 'localhost' in domain:
        domain = None

    if not token:
        refresh_token: str = await redis.get(access_token)
        if not refresh_token:
            raise ExpiredUserTokenException()

        token: types.RefreshTokenTD = await decode_token(
            refresh_token, a_s.REFRESH_TOKEN_SECRET_KEY
        )
        if not token:
            raise ExpiredUserTokenException()

        user = await get_user_info(db, token['email'])
        if not user:
            raise UserNotFoundException()

        await redis.delete(access_token)
        access_token, _ = await create_tokens_pair(
            user, user.role, request.headers.get('user-agent')
        )

        response.set_cookie(
            a_s.COOKIE_SESSION_KEY,
            access_token,
            expires=int(a_s.REFRESH_TOKEN_EXPIRES_MINUTES) * 60,

            domain=domain,
            httponly=True,
            samesite='none',
            secure=True
        )
        return user

    user = await get_user_info(db, token['email'])

    if not user:
        raise UserNotFoundException()

    role = await check_user_role_existence(
        db=db,
        role=token["role"]
    )
    if user.role != role.rolename:
        raise InvalidUserRoleException()

    response.set_cookie(
        a_s.COOKIE_SESSION_KEY,
        access_token,
        expires=int(a_s.REFRESH_TOKEN_EXPIRES_MINUTES) * 60,

        # domain=domain,
        # httponly=True,
        # samesite="none",
        # secure=True
    )
    return user


async def get_user_from_cookie(
    db: Annotated[AsyncSession, Depends(get_db)],
    request: Request,
    response: Response,
    access_token: types.AccessToken | None = Cookie(
        default=None,
        alias=a_s.COOKIE_SESSION_KEY
    )
) -> UserTTInfo | bool:

    if bool(int(a_s.SKIP_AUTH)):
        return True

    return await get_user_from_token(db, request, response, access_token)


async def get_user_from_header(
    db: Annotated[AsyncSession, Depends(get_db)],
    request: Request,
    response: Response,
    access_token: Annotated[
        types.AccessToken,
        Header(alias="Authorization")
    ],
) -> UserTTInfo:

    return await get_user_from_token(
        db, request, response, access_token.split(' ')[-1]
    )


async def logout(access_token: str) -> bool | None:

    try:
        await redis.delete(access_token)
    except aioredis.DataError:
        return True


async def login(
    db: AsyncSession,
    password: str,
    email: str,
    user_agent: str | None = None
) -> types.AccessToken:

    user = await get_user_by_email(db, email)
    if not user:
        raise UserNotFoundException()
    if not user.active:
        raise InactiveUserException(status_code=status.HTTP_401_UNAUTHORIZED)

    pass_is_valid = utils.verify_hash(password + user.pass_salt, user.password)
    if not pass_is_valid:
        raise InvalidLoginDataException()

    access_token, _ = await create_tokens_pair(
        user, user.role.rolename, user_agent
    )
    return access_token


async def get_active_user_from_header(
    user: Annotated[UserTTInfo, Depends(get_user_from_header)]
) -> UserTTInfo:

    if user and user.active:
        return user
    raise InactiveUserException()


async def get_active_user_from_cookie(
    user: Annotated[UserTTInfo, Depends(get_user_from_cookie)]
) -> UserTTInfo | bool:

    if bool(int(a_s.SKIP_AUTH)):

        return UserTTInfo(
            id=1,
            phone_number="+1234567890",
            organization_id=1,
            department_id=1,
            active=True,
            email='mock@mock.com',
            first_name='Mock',
            last_name='Mock',
            role=RoleType.HR_DIRECTOR,
            is_internal=True
        )

    if user and user.active:
        return user
    raise InactiveUserException()
