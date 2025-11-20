from enum import auto

from strenum import LowercaseStrEnum, MacroCaseStrEnum, StrEnum


class JobSiteMacroEnum(MacroCaseStrEnum):

    HEADHUNTER = auto()
    HUNTFLOW = auto()
    SUPERJOB = auto()


class JobSiteMicroEnum(LowercaseStrEnum):

    HEADHUNTER = auto()
    HUNTFLOW = auto()
    SUPERJOB = auto()


class IntegrationUserState(StrEnum):

    OK = auto()

    NEED_REAUTH = auto()
    USER_ACCOUNT_FORBIDDEN = auto()
    NETWORK_ERROR = auto()

    UNEXPECTED = auto()


class OrganizationBillingType(LowercaseStrEnum):

    FREE = auto()
    STANDARD = auto()
    PREMIUM = auto()


class UserAgreementType(StrEnum):

    EULA = auto()
