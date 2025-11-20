from enum import auto

from strenum import StrEnum


class LogFormatterType(StrEnum):

    COLORED_STR = auto()
    JSON = auto()


class LogHandlerType(StrEnum):

    STDOUT = auto()
