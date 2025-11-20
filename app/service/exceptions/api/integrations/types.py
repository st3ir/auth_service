from enum import auto

from strenum import MacroCaseStrEnum


class IntegrationExcState(MacroCaseStrEnum):

    UNEXPECTED = auto()
    USER_APP_CREDS_NOT_FOUND = auto()
    JOB_SITE_POLICY_NOT_FOUND = auto()
