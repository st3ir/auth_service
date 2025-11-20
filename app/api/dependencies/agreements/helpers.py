from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.users.agreements.schemas import BaseUserAgreementSchema
from api.users.schemas import UserTTInfo
from db.session import get_db
from service.auth.handlers import get_active_user_from_cookie
from service.exceptions.api.users.exc import AgreementAlreadyAcceptedException
from service.exceptions.api.users.msg import agreement_already_accepted_text
from service.users.models import UserAgreement


async def check_accepted_agreements(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserTTInfo, Depends(get_active_user_from_cookie)],
    user_agreement: BaseUserAgreementSchema
) -> BaseUserAgreementSchema:

    query = (
        select(UserAgreement)
        .where(
            UserAgreement.organization_id == user.organization_id,
            UserAgreement.user_id == user.id,
        )
    )
    result = (await db.execute(query)).scalars().all()

    for item in result:
        if item.agreement_type in user_agreement.agreement_types:
            raise AgreementAlreadyAcceptedException(
                exc_info=agreement_already_accepted_text.format(item.agreement_type)
            )

    return user_agreement
