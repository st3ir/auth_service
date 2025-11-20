import random

import factory

from service.rights.models import SpecRights, UserRights
from service.rights.types import RightType, SourceType
from tests.common.factories import (
    AsyncSQLAlchemyFactory,
    CommonMeta,
    JsonFactory,
)


class SpecRightsFactory(AsyncSQLAlchemyFactory):

    class Meta(CommonMeta):
        model = SpecRights

    id = factory.Sequence(lambda n: n + 100)
    source_id = factory.Sequence(lambda n: n + 100)

    @factory.lazy_attribute
    def source_type(self) -> str:

        types = [source for source in SourceType]
        return types[random.randint(0, len(types) - 1)]

    @factory.lazy_attribute
    def right_type(self) -> str:

        types = [right for right in RightType]
        return types[random.randint(0, len(types) - 1)]


class UserRightsFactory(AsyncSQLAlchemyFactory):

    class Meta(CommonMeta):
        model = UserRights

    id = factory.Sequence(lambda n: n + 100)

    subject_id = factory.Sequence(lambda n: n + 100)
    right_id = factory.Sequence(lambda n: n + 100)
    constraints = factory.Dict({}, dict_factory=JsonFactory)
