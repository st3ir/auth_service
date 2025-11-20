from fastapi import status

from service.exceptions.api.files import msg
from service.exceptions.api.files.types import FileExcState
from service.exceptions.exc import BaseApiException
from service.exceptions.msg import unexpected_error_text


class BaseFileException(BaseApiException):

    exc_state = FileExcState.UNEXPECTED
    exc_info = unexpected_error_text


class InvalidContentTypeException(BaseFileException):

    exc_state = FileExcState.INVALID_IMAGE_CONTENT_TYPE
    exc_info = msg.invalid_content_type_text
    status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


class FailedUploadImageException(BaseFileException):

    exc_state = FileExcState.FAILED_UPLOAD_IMAGE
    exc_info = msg.failed_upload_file_text
    status_code = status.HTTP_400_BAD_REQUEST


class MaxImageSizeExceededException(BaseFileException):

    exc_state = FileExcState.MAX_IMAGE_SIZE_EXCEEDED
    exc_info = msg.max_file_size_exceeded
    status_code = status.HTTP_400_BAD_REQUEST
