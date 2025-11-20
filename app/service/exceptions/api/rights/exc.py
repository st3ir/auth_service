from fastapi import status

from service.exceptions.api.rights import msg
from service.exceptions.api.rights.types import RightsExcState
from service.exceptions.exc import BaseApiException
from service.exceptions.msg import unexpected_error_text


class BaseRightsException(BaseApiException):

    exc_state = RightsExcState.UNEXPECTED
    exc_info = unexpected_error_text


class RightsNotFoundException(BaseRightsException):

    exc_state = RightsExcState.RIGHTS_NOT_FOUND
    exc_info = msg.rights_not_exists_text
    status_code = status.HTTP_404_NOT_FOUND


class RightsAlreadyExistsException(BaseRightsException):

    exc_state = RightsExcState.RIGHTS_ALREADY_EXISTS
    exc_info = msg.rights_already_exists_text
    status_code = status.HTTP_400_BAD_REQUEST


class InsufficientRightsException(BaseRightsException):

    exc_state = RightsExcState.INSUFFICIENT_RIGHTS
    exc_info = msg.insufficient_rights_text
    status_code = status.HTTP_403_FORBIDDEN
