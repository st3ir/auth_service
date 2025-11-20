import uuid

import pytest
from sqlalchemy import select

from service.helpers.utils import pwd_context
from service.users import models as user_models
from tests.conftest import async_session
from tests.service.organization.factories import DepartmentFactory, OrganizationFactory


@pytest.mark.asyncio
async def test_add_user():
    async with (async_session() as session):

        comp = await OrganizationFactory()
        department = await DepartmentFactory(organization_id=comp.id)

        email = "jonny@mail.com"
        pass_salt = uuid.uuid4().hex
        new_user = user_models.User(
            pass_salt=pass_salt,
            password=pwd_context.hash("testpassword" + pass_salt),
            email=email,
            active=True,
            first_name="John",
            last_name="Doe",
            department_id=department.id
        )
        session.add(new_user)

        query = (
            select(user_models.User)
            .where(user_models.User.email == email)
        )
        result = await session.execute(query)
        result = result.unique().all()
        assert len(result) == 1
        assert result[0][0].first_name == "John"
