from enum import auto

from strenum import MacroCaseStrEnum


class ExcState(MacroCaseStrEnum):

    UNEXPECTED = auto()


class ExcScope(MacroCaseStrEnum):

    INTERNAL = auto()

    RIGHTS = auto()
    FILES = auto()
    INTEGRATIONS = auto()
    ORGANIZATIONS = auto()
    USERS = auto()
