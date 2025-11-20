from fastapi import status

from service.exceptions import msg
from service.exceptions.types import ExcState


class BaseCustomException(Exception):

    exc_state = ExcState.UNEXPECTED
    exc_info = msg.internal_error_text

    def __init__(
        self,
        exc_state: str | None = None,
        exc_info: str | None = None,
    ) -> None:

        if exc_state:
            self.exc_state = exc_state

        if exc_info:
            self.exc_info = exc_info

    def __str__(self) -> str:

        return f"{self.exc_state}: {self.exc_info}"

    def exc_dump(self) -> dict:

        return {
            "exc_state": self.exc_state,
            "exc_info": self.exc_info
        }


class BaseServiceException(BaseCustomException):

    ...


class BaseApiException(BaseCustomException):

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self,
        exc_state: str | None = None,
        exc_info: str | None = None,
        status_code: int | None = None,
    ) -> None:
        super().__init__(exc_state, exc_info)

        if status_code:
            self.status_code = status_code
