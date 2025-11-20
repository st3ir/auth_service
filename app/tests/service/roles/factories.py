import random

import factory

from service.roles.models import Role, UserRole
from service.roles.types import RoleType
from tests.common.factories import AsyncSQLAlchemyFactory, CommonMeta


class RoleFactory(AsyncSQLAlchemyFactory):

    class Meta(CommonMeta):
        model = Role

    id = factory.Sequence(lambda n: n + 100)

    @factory.lazy_attribute
    def rolename(self) -> str:

        roles = [_role for _role in RoleType]
        return roles[random.randint(0, len(roles) - 1)]


class UserRoleFactory(AsyncSQLAlchemyFactory):

    class Meta(CommonMeta):
        model = UserRole

    id = factory.Sequence(lambda n: n + 100)

    role_id = factory.Sequence(lambda n: n + 100)
    user_id = factory.Sequence(lambda n: n + 100)
