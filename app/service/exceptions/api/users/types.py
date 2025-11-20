from enum import auto

from strenum import MacroCaseStrEnum


class UserExcState(MacroCaseStrEnum):

    UNEXPECTED = auto()

    INVALID_LOGIN_DATA = auto()
    INACTIVE_USER = auto()
    USER_NOT_FOUND = auto()
    INVALID_USER_ROLE = auto()
    USER_EMAIL_ALREADY_EXISTS = auto()

    INVALID_USER_TOKEN = auto()
    EXPIRED_USER_TOKEN = auto()

    AGREEMENT_ALREADY_ACCEPTED = auto()
    EULA_MUST_BE_ACCEPTED = auto()
    RIGHT_NOT_MATCHED_WITH_USER_ROLE = auto()
