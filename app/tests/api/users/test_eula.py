import pytest
from fastapi import status

from settings import auth_settings as a_s
from service.roles.types import RoleType
from service.types import UserAgreementType
from tests.constants import AGREEMENTS__ACCEPT_URL, USER__WHOAMI_URL
from tests.service.organization.factories import (
    DepartmentFactory,
    OrganizationFactory,
)
from tests.service.roles.factories import RoleFactory, UserRoleFactory
from tests.service.users.factories import UserAgreementFactory, UserFactory
from tests.user_access_token import get_user_access_token


@pytest.mark.asyncio
async def test_user_not_accepted_eula(fixture_client):

    org = await OrganizationFactory()
    department = await DepartmentFactory(organization_id=org.id)
    user = await UserFactory(department_id=department.id)
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

    assert response["is_eula_accepted"] is False


@pytest.mark.asyncio
async def test_user_accepted_eula(fixture_client):

    org = await OrganizationFactory()
    department = await DepartmentFactory(organization_id=org.id)
    user = await UserFactory(department_id=department.id)
    role = await RoleFactory(rolename=RoleType.HR_RECRUITER)
    await UserRoleFactory(user_id=user.id, role_id=role.id)
    await UserAgreementFactory(user_id=user.id, organization_id=org.id)

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

    assert response["is_eula_accepted"]


@pytest.mark.asyncio
async def test_user_accept_eula(fixture_client):

    org = await OrganizationFactory()
    department = await DepartmentFactory(organization_id=org.id)
    user = await UserFactory(department_id=department.id)
    role = await RoleFactory(rolename=RoleType.HR_RECRUITER)
    await UserRoleFactory(user_id=user.id, role_id=role.id)

    access_token, _ = await get_user_access_token(user, role)
    cookies = {a_s.COOKIE_SESSION_KEY: access_token}
    headers = {"Authorization": f'Bearer {access_token}'}
    json = {
        "agreement_types": [UserAgreementType.EULA]
    }

    response = await fixture_client.post(
        AGREEMENTS__ACCEPT_URL,
        cookies=cookies,
        headers=headers,
        json=json,
    )

    assert response.status_code == status.HTTP_200_OK

    response = response.json()
    assert response["is_accepted"]


@pytest.mark.asyncio
async def test_user_accept_eula_again(fixture_client):

    org = await OrganizationFactory()
    department = await DepartmentFactory(organization_id=org.id)
    user = await UserFactory(department_id=department.id)
    role = await RoleFactory(rolename=RoleType.HR_RECRUITER)
    await UserRoleFactory(user_id=user.id, role_id=role.id)
    await UserAgreementFactory(user_id=user.id, organization_id=org.id)

    access_token, _ = await get_user_access_token(user, role)
    cookies = {a_s.COOKIE_SESSION_KEY: access_token}
    headers = {"Authorization": f'Bearer {access_token}'}
    json = {
        "agreement_types": [UserAgreementType.EULA]
    }

    response = await fixture_client.post(
        AGREEMENTS__ACCEPT_URL,
        cookies=cookies,
        headers=headers,
        json=json,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_user_eula_mock_on(fixture_client):

    a_s.SKIP_AGREEMENT = 1

    org = await OrganizationFactory()
    department = await DepartmentFactory(organization_id=org.id)
    user = await UserFactory(department_id=department.id)
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

    assert response["is_eula_accepted"] is True


@pytest.mark.asyncio
async def test_user_eula_mock_off(fixture_client):

    a_s.SKIP_AGREEMENT = 0

    org = await OrganizationFactory()
    department = await DepartmentFactory(organization_id=org.id)
    user = await UserFactory(department_id=department.id)
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

    assert response["is_eula_accepted"] is False


@pytest.mark.asyncio
async def test_whoami_eula_mock_on(
    fixture_authorized_user_without_eula
):
    a_s.SKIP_AGREEMENT = 1

    response = await fixture_authorized_user_without_eula.get("client").get(
        USER__WHOAMI_URL
    )

    assert response.status_code == 200

    info = response.json()

    assert info['is_eula_accepted'] is True


@pytest.mark.asyncio
async def test_whoami_eula_mock_off(
    fixture_authorized_user_without_eula
):
    a_s.SKIP_AGREEMENT = 0

    response = await fixture_authorized_user_without_eula.get("client").get(
        USER__WHOAMI_URL
    )

    assert response.status_code == 200

    info = response.json()

    assert info['is_eula_accepted'] is False
