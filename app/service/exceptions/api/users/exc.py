from fastapi import status

from service.exceptions.api.users import msg
from service.exceptions.api.users.types import UserExcState
from service.exceptions.exc import BaseApiException
from service.exceptions.msg import unexpected_error_text


class BaseUserException(BaseApiException):

    exc_state = UserExcState.UNEXPECTED
    exc_info = unexpected_error_text


class UserEmailAlreadyExistsException(BaseUserException):

    exc_state = UserExcState.USER_EMAIL_ALREADY_EXISTS
    exc_info = msg.user_email_already_exists_text
    status_code = status.HTTP_400_BAD_REQUEST


class InactiveUserException(BaseUserException):

    exc_state = UserExcState.INACTIVE_USER
    exc_info = msg.inactive_user_text
    status_code = status.HTTP_403_FORBIDDEN


class InvalidUserRoleException(BaseUserException):

    exc_state = UserExcState.INVALID_USER_ROLE
    exc_info = msg.invalid_user_role_text
    status_code = status.HTTP_400_BAD_REQUEST


class UserNotFoundException(BaseUserException):

    exc_state = UserExcState.USER_NOT_FOUND
    exc_info = msg.user_not_found_text
    status_code = status.HTTP_401_UNAUTHORIZED


class InvalidUserTokenException(BaseUserException):

    exc_state = UserExcState.INVALID_USER_TOKEN
    exc_info = msg.invalid_user_token_text
    status_code = status.HTTP_401_UNAUTHORIZED


class ExpiredUserTokenException(BaseUserException):

    exc_state = UserExcState.EXPIRED_USER_TOKEN
    exc_info = msg.expired_user_token_text
    status_code = status.HTTP_401_UNAUTHORIZED


class InvalidLoginDataException(BaseUserException):

    exc_state = UserExcState.INVALID_LOGIN_DATA
    exc_info = msg.invalid_login_data_text
    status_code = status.HTTP_401_UNAUTHORIZED


class AgreementAlreadyAcceptedException(BaseUserException):

    exc_state = UserExcState.AGREEMENT_ALREADY_ACCEPTED
    exc_info = msg.agreement_already_accepted_text
    status_code = status.HTTP_400_BAD_REQUEST


class EulaMustBeAcceptedException(BaseUserException):

    exc_state = UserExcState.EULA_MUST_BE_ACCEPTED
    exc_info = msg.eula_must_be_accepted_text
    status_code = status.HTTP_403_FORBIDDEN


class RightNotMatchWithUserRole(BaseUserException):

    exc_state = UserExcState.RIGHT_NOT_MATCHED_WITH_USER_ROLE
    exc_info = msg.right_not_match_with_role_text
    status_code = status.HTTP_400_BAD_REQUEST
