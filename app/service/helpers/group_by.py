from typing import Sequence

from sqlalchemy.engine.row import RowMapping
from operator import attrgetter
from itertools import groupby


async def group_rows_by_field(
    sequence: Sequence[RowMapping],
    field: str,
    needed_event_type: str | int | None = None
) -> dict[str, list[RowMapping]]:

    return {
        event_type: list(item)
        for event_type, item
        in groupby(sequence, attrgetter(field))
        if (
            not needed_event_type
            or (needed_event_type and event_type == needed_event_type)
        )
    }
