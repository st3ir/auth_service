from pydantic import BaseModel

from service.types import UserAgreementType


class BaseUserAgreementSchema(BaseModel):

    agreement_types: list[UserAgreementType] | None = []
