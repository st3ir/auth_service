import pytest
from fastapi import status

from service.helpers import utils
from service.roles.types import RoleType
from settings import auth_settings as a_s
from tests.constants import USER__WHOAMI_URL
from tests.service.organization.factories import OrganizationFactory, DepartmentFactory
from tests.service.roles.factories import RoleFactory, UserRoleFactory
from tests.service.users.factories import UserFactory
from tests.user_access_token import get_user_access_token


@pytest.mark.asyncio
async def test_get_active_user(
    fixture_authorized_user
):
    user = fixture_authorized_user.get("user")
    response = await fixture_authorized_user.get("client").get(
        USER__WHOAMI_URL
    )

    assert response.status_code == 200

    info = response.json()
    assert info['first_name'] == user.first_name
    assert info['last_name'] == user.last_name
    assert info['email'] == user.email


@pytest.mark.asyncio
async def test_get_inactive_user(
    fixture_client, fixture_inactive_user
):
    user = fixture_inactive_user.get("user")
    cookie = utils.create_token(
        {
            "email": user.email,
            "user_id": user.id,
            "role": fixture_inactive_user.get("role").rolename,
        },
        minutes=int(a_s.ACCESS_TOKEN_EXPIRES_MINUTES),
        secret_key=a_s.ACCESS_TOKEN_SECRET_KEY,
        algorithm=a_s.TOKENS_ALGORITHM,
    )
    cookies = {a_s.COOKIE_SESSION_KEY: cookie}

    response = await fixture_client.get(
        USER__WHOAMI_URL,
        cookies=cookies
    )

    assert response.status_code == 403
    fixture_client.cookies = None


@pytest.mark.asyncio
async def test_check_is_internal_true(
    fixture_authorized_user
):

    response = await fixture_authorized_user.get("client").get(
        USER__WHOAMI_URL
    )

    assert response.status_code == 200

    info = response.json()
    assert info['is_internal'] is True


@pytest.mark.asyncio
async def test_check_is_internal_false(fixture_client):

    org = await OrganizationFactory()
    department = await DepartmentFactory(organization_id=org.id)
    user = await UserFactory(department_id=department.id, is_internal=False)
    role = await RoleFactory(rolename=RoleType.HR_RECRUITER)
    await UserRoleFactory(user_id=user.id, role_id=role.id)

    access_token, _ = await get_user_access_token(user, role)
    cookies = {a_s.COOKIE_SESSION_KEY: access_token}
    headers = {"Authorization": f'Bearer {access_token}'}

    response = await fixture_client.get(
        USER__WHOAMI_URL,
        cookies=cookies,
        headers=headers
    )

    assert response.status_code == status.HTTP_200_OK
    response = response.json()

    assert response["is_internal"] is False
