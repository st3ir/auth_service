from enum import auto

from strenum import MacroCaseStrEnum


class FileExcState(MacroCaseStrEnum):

    UNEXPECTED = auto()

    INVALID_IMAGE_CONTENT_TYPE = auto()
    FAILED_UPLOAD_IMAGE = auto()
    MAX_IMAGE_SIZE_EXCEEDED = auto()
