import pytest
from httpx import AsyncClient

from main import app
from service.roles.types import RoleType
from settings import auth_settings as a_s
from tests.conftest import factory_session
from tests.service.organization.factories import (
    DepartmentFactory,
    OrganizationFactory,
)
from tests.service.roles.factories import RoleFactory, UserRoleFactory
from tests.service.users.factories import UserAgreementFactory, UserFactory
from tests.user_access_token import get_user_access_token


@pytest.fixture(scope="function")
async def fixture_organization():

    organization = OrganizationFactory()
    department = DepartmentFactory(organization_id=organization.id)

    info = {
        "organization": organization,
        "department": department
    }

    factory_session.expunge_all()

    return info


@pytest.fixture(scope="function")
async def fixture_authorized_user():

    org = await OrganizationFactory()
    department = await DepartmentFactory(organization_id=org.id)
    user = await UserFactory(department_id=department.id)
    role = await RoleFactory(rolename=RoleType.HR_RECRUITER)
    await UserAgreementFactory(user_id=user.id, organization_id=org.id)
    await UserRoleFactory(user_id=user.id, role_id=role.id)

    access_token, refresh_token = await get_user_access_token(user, role)
    cookies = {a_s.COOKIE_SESSION_KEY: access_token}
    headers = {"Authorization": f'Bearer {access_token}'}

    async with AsyncClient(
        app=app, base_url="http://test",
        cookies=cookies, headers=headers
    ) as ac:
        info = {
            "client": ac,
            "user": user,
            "department": department,
            "organization": org,
            "role": role
        }
        yield info


@pytest.fixture(scope="function")
async def fixture_authorized_user_without_eula():

    org = await OrganizationFactory()
    department = await DepartmentFactory(organization_id=org.id)
    user = await UserFactory(department_id=department.id)
    role = await RoleFactory(rolename=RoleType.HR_RECRUITER)
    await UserRoleFactory(user_id=user.id, role_id=role.id)

    access_token, refresh_token = await get_user_access_token(user, role)
    cookies = {a_s.COOKIE_SESSION_KEY: access_token}
    headers = {"Authorization": f'Bearer {access_token}'}

    async with AsyncClient(
        app=app, base_url="http://test",
        cookies=cookies, headers=headers
    ) as ac:
        info = {
            "client": ac,
            "user": user,
            "department": department,
            "organization": org,
            "role": role
        }
        yield info


@pytest.fixture(scope="function")
async def fixture_inactive_user():
    org = await OrganizationFactory()
    department = await DepartmentFactory(organization_id=org.id)
    user = await UserFactory(department_id=department.id, active=False)
    role = await RoleFactory()
    await UserAgreementFactory(user_id=user.id, organization_id=org.id)
    await UserRoleFactory(user_id=user.id, role_id=role.id)

    info = {
        "user": user,
        "department": department,
        "organization": org,
        "role": role
    }
    return info


@pytest.fixture(scope="function")
async def fixture_authorized_hr_employee_user():

    org = await OrganizationFactory(full_name="pepe", short_name="PEPE")
    department = await DepartmentFactory(organization_id=org.id)
    user = await UserFactory(department_id=department.id)
    role = await RoleFactory(rolename=RoleType.HR_EMPLOYEE)
    await UserAgreementFactory(user_id=user.id, organization_id=org.id)
    await UserRoleFactory(user_id=user.id, role_id=role.id)

    access_token, refresh_token = await get_user_access_token(user, role)
    cookies = {a_s.COOKIE_SESSION_KEY: access_token}
    headers = {"Authorization": f'Bearer {access_token}'}

    async with AsyncClient(
        app=app, base_url="http://test",
        cookies=cookies, headers=headers
    ) as ac:
        info = {
            "client": ac,
            "user": user,
            "department": department,
            "organization": org,
            "role": role
        }
        yield info


@pytest.fixture(scope="function")
async def fixture_user():
    org = await OrganizationFactory()
    department = await DepartmentFactory(organization_id=org.id)
    user = await UserFactory(department_id=department.id)
    role = await RoleFactory()
    await UserRoleFactory(user_id=user.id, role_id=role.id)

    info = {
        "user": user,
        "department": department,
        "organization": org,
        "role": role
    }

    return info
