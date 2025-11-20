from logging import config

import click

from lib.cli.migrate.huntflow.handlers import migrate_data_from_hf_by_type
from lib.cli.migrate.types import MigrateSourceType
from lib.log.settings import LogSettings

config.dictConfig(LogSettings().build())


@click.group()
def cli():

    ...


@click.command('migrate-from-huntflow')
@click.option(
    '--filepath', '-f',
    prompt='File path',
    help='File to migrate departments from HF'
)
@click.option(
    '--organization_id', '-o',
    prompt='Organization ID',
    type=int
)
def migrate_department_from_huntflow(
    filepath: str,
    organization_id: int,
    source_type: MigrateSourceType = MigrateSourceType.DEPARTMENT
) -> None:

    if not filepath:
        click.ClickException('Skip. Arg filepath so empty')

    migrate_data_from_hf_by_type(**locals())


cli.add_command(migrate_department_from_huntflow)


if __name__ == '__main__':

    cli()
