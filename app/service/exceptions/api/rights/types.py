from enum import auto

from strenum import MacroCaseStrEnum


class RightsExcState(MacroCaseStrEnum):

    UNEXPECTED = auto()

    RIGHTS_NOT_FOUND = auto()
    RIGHTS_ALREADY_EXISTS = auto()
    INSUFFICIENT_RIGHTS = auto()
