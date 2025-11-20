from fastapi import status

from service.exceptions.api.integrations import msg
from service.exceptions.api.integrations.types import IntegrationExcState
from service.exceptions.exc import BaseApiException
from service.exceptions.msg import unexpected_error_text


class BaseIntegrationException(BaseApiException):

    exc_state = IntegrationExcState.UNEXPECTED
    exc_info = unexpected_error_text


class UserAppCredentialsNotFoundException(BaseIntegrationException):

    exc_state = IntegrationExcState.USER_APP_CREDS_NOT_FOUND
    exc_info = msg.user_app_creds_not_found_text
    status_code = status.HTTP_404_NOT_FOUND


class JobSitePolicyNotFoundException(BaseIntegrationException):

    exc_state = IntegrationExcState.JOB_SITE_POLICY_NOT_FOUND
    exc_info = msg.job_site_policy_not_found_text
    status_code = status.HTTP_404_NOT_FOUND
