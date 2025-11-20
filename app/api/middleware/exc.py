import logging
from typing import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from service.exceptions import msg
from service.exceptions.api.files import BaseFileException
from service.exceptions.api.integrations import BaseIntegrationException
from service.exceptions.api.organizations import BaseOrganizationException
from service.exceptions.api.rights import BaseRightsException
from service.exceptions.api.users import BaseUserException
from service.exceptions.exc import BaseApiException, BaseServiceException
from service.exceptions.types import ExcScope, ExcState

logger = logging.getLogger(__name__)


class HTTPExceptionMiddleware(BaseHTTPMiddleware):

    def handle_svc_exc(
        self,
        exc_info: dict,
        exc: BaseApiException | BaseServiceException,
        scope: ExcScope = ExcScope.INTERNAL
    ) -> dict:

        exc_info.update(exc.exc_dump())
        exc_info["exc_scope"] = scope
        exc_info["code"] = (
            exc.status_code if hasattr(exc, "status_code") else exc_info["code"]
        )

        return exc_info

    async def dispatch(
            self,
            request: Request,
            call_next: Callable
    ) -> JSONResponse:

        exc_info = {
            "exc_scope": ExcScope.INTERNAL,
            "exc_state": ExcState.UNEXPECTED,
            "exc_info": msg.internal_error_text,
            "code": HTTP_500_INTERNAL_SERVER_ERROR
        }

        try:
            return await call_next(request)

        except BaseFileException as exc:
            exc_info = self.handle_svc_exc(exc_info, exc, ExcScope.FILES)

        except BaseIntegrationException as exc:
            exc_info = self.handle_svc_exc(exc_info, exc, ExcScope.INTEGRATIONS)

        except BaseOrganizationException as exc:
            exc_info = self.handle_svc_exc(exc_info, exc, ExcScope.ORGANIZATIONS)

        except BaseRightsException as exc:
            exc_info = self.handle_svc_exc(exc_info, exc, ExcScope.RIGHTS)

        except BaseUserException as exc:
            exc_info = self.handle_svc_exc(exc_info, exc, ExcScope.USERS)

        except (BaseServiceException, BaseApiException) as exc:
            exc_info = self.handle_svc_exc(exc_info, exc)

        except Exception as exc:
            logger.exception(exc, exc_info=True)

        return JSONResponse(
            exc_info,
            status_code=exc_info.pop("code")
        )
