import datetime
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from api.users import schemas as user_schemas
from db.session import get_db
from service.auth import handlers
from service.helpers.url_utils import extract_base_url
from settings import auth_settings as a_s

api_router = APIRouter()


@api_router.post(
    "/auth",
    status_code=status.HTTP_200_OK,
    response_model=user_schemas.UserTTInfo,
)
async def login(
    response: Response,
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):

    origin = extract_base_url(request.headers.get('origin'))
    referer = extract_base_url(request.headers.get('referer'))
    host = extract_base_url(request.headers.get('host'))
    user_agent = request.headers.get('user-agent')

    domain = f'{origin or referer or host or a_s.DOMAIN_URL}'
    if 'localhost' in domain:
        domain = None

    access_token = await handlers.login(
        db=db,
        password=form_data.password,
        email=form_data.username,
        user_agent=user_agent
    )

    response.set_cookie(
        a_s.COOKIE_SESSION_KEY,
        access_token,
        expires=int(a_s.REFRESH_TOKEN_EXPIRES_MINUTES) * 60,

        domain=domain,
        httponly=True,
        samesite="none",
        secure=True
    )
    return await handlers.get_user_info(db, form_data.username)


@api_router.delete(
    "/logout",
    status_code=status.HTTP_200_OK
)
async def logout(
    response: Response,
    request: Request,
    access_token: str | None = Cookie(
        default=None, alias=a_s.COOKIE_SESSION_KEY
    )
):

    if bool(int(a_s.SKIP_AUTH)):
        return True

    origin = extract_base_url(request.headers.get('origin'))
    referer = extract_base_url(request.headers.get('referer'))
    host = extract_base_url(request.headers.get('host'))

    domain = f'{origin or referer or host or a_s.DOMAIN_URL}'

    if 'localhost' in domain:
        domain = None

    await handlers.logout(access_token=access_token)

    expires = datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=1)
    resp = JSONResponse(status_code=status.HTTP_200_OK, content='Ok')
    resp.set_cookie(
        a_s.COOKIE_SESSION_KEY,
        '',
        secure=True,
        httponly=True,
        samesite='none',
        expires=expires,
        domain=domain
    )
    return resp
