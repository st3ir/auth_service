from enum import auto

from strenum import MacroCaseStrEnum


class OrganizationExcState(MacroCaseStrEnum):

    UNEXPECTED = auto()
    DEPARTMENT_NOT_FOUND = auto()
