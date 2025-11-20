from enum import IntEnum, auto

from strenum import LowercaseStrEnum, MacroCaseStrEnum, UppercaseStrEnum

from service.roles.types import RoleType


class SourceType(MacroCaseStrEnum):

    USER = auto()

    VACANCY = auto()
    VACANCY_REQUEST = auto()

    RESUME = auto()
    CANDIDATURE = auto()


class RightType(UppercaseStrEnum):

    VIEW_PUBLIC = auto()
    VIEW_ALL = auto()

    MANAGE = auto()
    DELETE = auto()


class RightScoreType(IntEnum):

    VIEW_PUBLIC = 1
    VIEW_ALL = auto()

    MANAGE = auto()
    DELETE = auto()


class HiddenFieldsVacancy(LowercaseStrEnum):

    SALARY_FROM = auto()
    SALARY_TO = auto()


ROLE_TO_RIGHTS_MAP = {
    RoleType.SERVICE_USER: [RightType.DELETE],
    RoleType.USER_MASTER: [RightType.DELETE],
    RoleType.HR_DIRECTOR: [RightType.DELETE],
    RoleType.HR_RECRUITER: [RightType.MANAGE, RightType.VIEW_ALL],
    RoleType.HR_SENIOR_EMPLOYEE: [RightType.VIEW_PUBLIC, RightType.VIEW_ALL],
    RoleType.HR_EMPLOYEE: [RightType.VIEW_PUBLIC],
}
