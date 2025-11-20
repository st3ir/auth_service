import asyncio

from lib.cli.migrate.types import MigrateSourceType
from lib.cli.migrate.huntflow.departments.handlers import migrate_departments_from_hf

loop = asyncio.get_event_loop()


def migrate_data_from_hf_by_type(
    filepath: str,
    organization_id: int,
    source_type: MigrateSourceType.DEPARTMENT,
) -> None:

    type_handler_map = {
        MigrateSourceType.DEPARTMENT: migrate_departments_from_hf
    }

    hf_handler = type_handler_map[source_type]
    loop.run_until_complete(hf_handler(filepath, organization_id))
