from sqlalchemy.ext.asyncio import AsyncSession

from api.users.schemas import UserTTInfo
from db.utils.transactional import transaction
from service.types import UserAgreementType
from service.users.models import UserAgreement


async def accept_agreements(
    db: AsyncSession,
    user: UserTTInfo,
    agreements: list[UserAgreementType]
) -> None:

    new_agreements = []
    for item in agreements:
        new_agreements.append(
            UserAgreement(
                user_id=user.id,
                organization_id=user.organization_id,
                agreement_type=item
            )
        )

    async with transaction(db):
        db.add_all(new_agreements)
