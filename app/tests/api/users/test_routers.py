import random

import pytest

from settings import main_settings as m_s
from service.roles.types import RoleType
from tests.constants import USER__WHOAMI_URL
from tests.service.organization.factories import (
    DepartmentFactory,
    OrganizationFactory
)
from tests.service.roles.factories import UserRoleFactory
from tests.service.users.factories import UserFactory


@pytest.mark.asyncio
async def test_get_active_user(fixture_authorized_user):
    user = fixture_authorized_user.get("user")
    response = await fixture_authorized_user.get("client").get(
        USER__WHOAMI_URL
    )

    assert response.status_code == 200

    info = response.json()
    assert info['first_name'] == user.first_name
    assert info['last_name'] == user.last_name
    assert info['email'] == user.email
    assert info['department_id'] == user.department_id


@pytest.mark.asyncio
async def test_create_user(
    fixture_authorized_user
):
    user = {
        "first_name": "test",
        "last_name": "user",
        "email": "test@test.com",
        "password": "testtest1",
        "active": True,
        "firstname": "test",
        "surname": "user",
    }

    params = {
        "role": RoleType.HR_RECRUITER,
    }

    response = await fixture_authorized_user.get("client").post(
        f"{m_s.USE_PREFIX}/users",
        data=user,
        params=params
    )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_update_user(
    fixture_authorized_user
):
    user = await UserFactory()
    updated_info = {
        "first_name": "test",
        "last_name": "user",
        "email": "test@test.com",
    }

    params = {
        "role": RoleType.HR_RECRUITER,
    }

    response = await fixture_authorized_user.get("client").put(
        f"{m_s.USE_PREFIX}/users/{user.id}",
        data=updated_info,
        params=params
    )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_get_users_by_role(fixture_authorized_user):
    department = fixture_authorized_user.get("department")

    org2 = await OrganizationFactory(
        full_name="FACTORY_ORGANIZATION2",
        short_name="2FACTORY_ORGANIZATION2",
    )
    dep2 = await DepartmentFactory(organization_id=org2.id)
    user_dep2 = await UserFactory.create_batch(size=3, department_id=dep2.id)

    user = await UserFactory(department_id=department.id)
    await UserRoleFactory(
        role_id=fixture_authorized_user["role"].id,
        user_id=user.id
    )

    for user in user_dep2:
        await UserRoleFactory(
            role_id=fixture_authorized_user["role"].id, user_id=user.id
        )

    params = {
        "roles": [RoleType.HR_RECRUITER]
    }
    response = await fixture_authorized_user.get("client").get(
        f'{m_s.USE_PREFIX}/users/by-roles',
        params=params
    )

    assert response.status_code == 200
    content = response.json()
    assert len(content) == 2


@pytest.mark.asyncio
async def test_get_users_by_role_empty(fixture_authorized_user):

    user = await UserFactory()
    await UserRoleFactory(
        role_id=fixture_authorized_user["role"].id,
        user_id=user.id
    )

    params = {
        "roles": [RoleType.HR_DIRECTOR]
    }
    response = await fixture_authorized_user.get("client").get(
        f'{m_s.USE_PREFIX}/users/by-roles',
        params=params
    )

    assert response.status_code == 200
    content = response.json()
    assert len(content) == 0


@pytest.mark.asyncio
async def test_get_users_by_role_bad_rolename(
        fixture_authorized_user
):

    user = await UserFactory()
    await UserRoleFactory(
        role_id=fixture_authorized_user["role"].id,
        user_id=user.id
    )

    params = {
        "roles": ["test"]
    }
    response = await fixture_authorized_user.get("client").get(
        f'{m_s.USE_PREFIX}/users/by-roles',
        params=params
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_users_by_ids(fixture_authorized_user):
    department = fixture_authorized_user.get("department")
    users = await UserFactory.create_batch(10, department_id=department.id)
    for user in users:
        await UserRoleFactory(
            role_id=fixture_authorized_user["role"].id, user_id=user.id
        )

    users_ids = list({user.id for user in users})
    params = {
        "user_ids": users_ids
    }
    response = await fixture_authorized_user.get("client").get(
        f'{m_s.USE_PREFIX}/users/by-ids',
        params=params
    )

    assert response.status_code == 200
    content = response.json()
    assert len(content) == 10


@pytest.mark.asyncio
async def test_get_users_by_ids_with_not_found_id(
    fixture_authorized_user
):
    department = fixture_authorized_user.get("department")
    users = await UserFactory.create_batch(10, department_id=department.id)
    for user in users:
        await UserRoleFactory(
            role_id=fixture_authorized_user["role"].id, user_id=user.id
        )

    users_ids = [user.id for user in users]
    users_ids.append(random.randint(1, 10))
    params = {
        "user_ids": users_ids
    }
    response = await fixture_authorized_user.get("client").get(
        f'{m_s.USE_PREFIX}/users/by-ids',
        params=params
    )

    assert response.status_code == 200
    content = response.json()
    assert len(content) == 10


@pytest.mark.asyncio
async def test_get_users_by_ids_with_duplicate_id(
    fixture_authorized_user
):
    department = fixture_authorized_user.get("department")
    users = await UserFactory.create_batch(10, department_id=department.id)
    for user in users:
        await UserRoleFactory(
            role_id=fixture_authorized_user["role"].id, user_id=user.id
        )

    users_ids = [user.id for user in users]
    users_ids.append(users_ids[0])
    params = {
        "user_ids": users_ids
    }
    response = await fixture_authorized_user.get("client").get(
        f'{m_s.USE_PREFIX}/users/by-ids',
        params=params
    )

    assert response.status_code == 200
    content = response.json()
    assert len(content) == 10
