from enum import auto
from strenum import MacroCaseStrEnum


class RoleType(MacroCaseStrEnum):

    HR_RECRUITER = auto()
    HR_SENIOR_EMPLOYEE = auto()
    HR_DIRECTOR = auto()

    USER_MASTER = auto()
    HR_EMPLOYEE = auto()

    SERVICE_USER = auto()
