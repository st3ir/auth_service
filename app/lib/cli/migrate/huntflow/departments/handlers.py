from contextlib import closing

import ijson

from db.session import get_db
from service.organizations.handlers import upsert_departments_by_organization


async def migrate_departments_from_hf(filepath: str, organization_id: int) -> None:

    with closing(open(filepath, 'rb')) as f:
        async for db in get_db():

            await upsert_departments_by_organization(
                db,
                organization_id,
                {
                    str(d['id']): d['name'] for d in ijson.items(f, 'items.item')
                }
            )
