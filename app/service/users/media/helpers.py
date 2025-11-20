from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from service.users.models import User


async def get_user_image_name(
    db: AsyncSession,
    user_id: UUID4
) -> str | None:

    img_exp = await db.execute(
        select(User.photo_link)
        .where(User.id == user_id),
    )
    img_link: str = img_exp.scalars().one_or_none()
    if img_link:
        return img_link
