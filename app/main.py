import logging.config

from fastapi import APIRouter, FastAPI
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from settings import main_settings as m_s
from api.auth.routers import api_router as auth_router
from api.middleware.exc import HTTPExceptionMiddleware
from api.organizations.routers import api_router as organizations_router
from api.users.agreements.routers import api_router as agreement_router
from api.users.integrations.routers import (
    api_router as user_integration_router,
)
from api.users.rights.routers import api_router as user_rights_router
from api.users.routers import api_router as user_router
from lib.log.settings import LogSettings

logging.config.dictConfig(LogSettings().build())


middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=m_s.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
]


app = FastAPI(
    title="auth-backend",
    middleware=middleware,
    openapi_url=f'{m_s.USE_PREFIX}/openapi.json',
    docs_url=f'{m_s.USE_PREFIX}/docs'
)
app.add_middleware(HTTPExceptionMiddleware)

main_api_router = APIRouter()
main_api_router.include_router(
    user_router,
    prefix=m_s.USE_PREFIX,
    tags=["User"]
)
main_api_router.include_router(
    user_rights_router,
    prefix=m_s.USE_PREFIX,
    tags=["Rights flow. SHOW & GRANT"]
)

main_api_router.include_router(
    user_integration_router,
    prefix=m_s.USE_PREFIX,
    tags=["User info with External API Credentials"]
)

main_api_router.include_router(
    auth_router,
    prefix=m_s.USE_PREFIX,
    tags=["Auth"]
)

main_api_router.include_router(
    organizations_router,
    prefix=m_s.USE_PREFIX,
    tags=["Organizations"]
)

main_api_router.include_router(
    agreement_router,
    prefix=m_s.USE_PREFIX,
    tags=["Agreements"]
)

app.include_router(main_api_router)
