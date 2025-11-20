from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.agreements.helpers import check_accepted_agreements
from api.users.agreements.schemas import BaseUserAgreementSchema
from api.users.schemas import UserTTInfo
from db.session import get_db
from service.auth.handlers import get_active_user_from_cookie
from service.users.agreements.handlers import accept_agreements

api_router = APIRouter(prefix='/agreements')


@api_router.post(
    "/accept",
    status_code=status.HTTP_200_OK,
    response_model=None
)
async def accept_agreement(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserTTInfo, Depends(get_active_user_from_cookie)],
    user_agreement: Annotated[
        BaseUserAgreementSchema,
        Depends(check_accepted_agreements)
    ],
):

    await accept_agreements(db, user, user_agreement.agreement_types)

    return {"is_accepted": True}
