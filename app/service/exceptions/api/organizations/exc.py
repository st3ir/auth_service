from fastapi import status

from service.exceptions.api.organizations import msg
from service.exceptions.api.organizations.types import OrganizationExcState
from service.exceptions.exc import BaseApiException
from service.exceptions.msg import unexpected_error_text


class BaseOrganizationException(BaseApiException):

    exc_state = OrganizationExcState.UNEXPECTED
    exc_info = unexpected_error_text


class DepartmentNotFoundException(BaseOrganizationException):

    exc_state = OrganizationExcState.DEPARTMENT_NOT_FOUND
    exc_info = msg.department_not_found
    status_code = status.HTTP_404_NOT_FOUND
