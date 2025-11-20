import pytest
from fastapi import status

from service.rights.types import RightType, SourceType
from service.types import IntegrationUserState, JobSiteMacroEnum, OrganizationBillingType
from settings import main_settings as m_s
from tests.service.organization.factories import (
    DepartmentFactory,
    JobSitePolicyFactory,
    OrganizationFactory,
)
from tests.service.rights.factories import SpecRightsFactory, UserRightsFactory
from tests.service.users.factories import JobSiteCredentialsFactory, UserFactory


@pytest.mark.asyncio
async def test_get_user_with_creds_positive(fixture_authorized_user):

    org = await OrganizationFactory(
        full_name="123",
        short_name="123"
    )
    dep = await DepartmentFactory(
        full_name="123",
        short_name="123",
        organization_id=org.id
    )
    user = await UserFactory(department_id=dep.id)
    await JobSiteCredentialsFactory(user_id=user.id)
    spec = await SpecRightsFactory(
        source_type=SourceType.VACANCY,
        right_type=RightType.MANAGE
    )
    await UserRightsFactory(
        subject_id=user.id,
        right_id=spec.id
    )

    response = await fixture_authorized_user.get("client").get(
        f"{m_s.USE_PREFIX}/integrations/users/with-creds",
        params={
            "user_id": user.id,
            "vacancy_id": spec.source_id
        }
    )

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) == 1

    assert result[0].get("user_id") == user.id
    assert result[0].get("is_priority")


@pytest.mark.asyncio
async def test_get_user_with_creds_negative(fixture_authorized_user):

    org = await OrganizationFactory(
        full_name="123",
        short_name="123"
    )
    dep = await DepartmentFactory(
        full_name="123",
        short_name="123",
        organization_id=org.id
    )
    user = await UserFactory(department_id=dep.id)
    await JobSiteCredentialsFactory(user_id=user.id)
    spec = await SpecRightsFactory(
        source_type=SourceType.VACANCY,
        right_type=RightType.VIEW_PUBLIC
    )
    await UserRightsFactory(
        subject_id=user.id,
        right_id=spec.id
    )

    response = await fixture_authorized_user.get("client").get(
        f"{m_s.USE_PREFIX}/integrations/users/with-creds",
        params={
            "user_id": user.id,
            "vacancy_id": spec.source_id
        }
    )

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) == 1

    assert result[0].get("user_id") == user.id
    assert not result[0].get("is_priority")


@pytest.mark.asyncio
async def test_get_two_user_with_creds(fixture_authorized_user):

    org = await OrganizationFactory(
        full_name="123",
        short_name="123"
    )
    dep = await DepartmentFactory(
        full_name="123",
        short_name="123",
        organization_id=org.id
    )
    user_1 = await UserFactory(department_id=dep.id)
    user_2 = await UserFactory(department_id=dep.id)
    await JobSiteCredentialsFactory(user_id=user_1.id)
    await JobSiteCredentialsFactory(user_id=user_2.id)

    spec_1 = await SpecRightsFactory(
        source_type=SourceType.VACANCY,
        right_type=RightType.MANAGE,
        source_id=1
    )
    await UserRightsFactory(
        subject_id=user_1.id,
        right_id=spec_1.id
    )

    response = await fixture_authorized_user.get("client").get(
        f"{m_s.USE_PREFIX}/integrations/users/with-creds",
        params={
            "user_id": user_1.id,
            "vacancy_id": 1
        }
    )

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) == 2

    expected = {user_1.id: True, user_2.id: False}

    first = result[0]
    assert first["is_priority"] == expected[first["user_id"]]
    second = result[1]
    assert second["is_priority"] == expected[second["user_id"]]


@pytest.mark.asyncio
async def test_get_user_without_creds(fixture_authorized_user):

    org = await OrganizationFactory(
        full_name="123",
        short_name="123"
    )
    dep = await DepartmentFactory(
        full_name="123",
        short_name="123",
        organization_id=org.id
    )
    user = await UserFactory(department_id=dep.id)

    response = await fixture_authorized_user.get("client").get(
        f"{m_s.USE_PREFIX}/integrations/users/with-creds",
        params={
            "user_id": user.id,
            "vacancy_id": 1
        }
    )

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) == 0


@pytest.mark.asyncio
async def test_update_user_integration_state_positive(fixture_authorized_user):

    org = await OrganizationFactory(
        full_name="123",
        short_name="123"
    )
    dep = await DepartmentFactory(
        full_name="123",
        short_name="123",
        organization_id=org.id
    )
    user = await UserFactory(department_id=dep.id)
    await JobSiteCredentialsFactory(
        user_id=user.id,
        credentials={
            "user_state": {
                "state": IntegrationUserState.NEED_REAUTH,
                "reason": "TEST"
            }
        },
        platform_type=JobSiteMacroEnum.HEADHUNTER,
    )
    json_ = {
        "state": IntegrationUserState.OK,
        "reason": "TEST"
    }

    response = await fixture_authorized_user.get("client").put(
        (
            f"{m_s.USE_PREFIX}/integrations/{JobSiteMacroEnum.HEADHUNTER.lower()}"
            f"/{user.id}/state"
        ),
        json=json_
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_update_user_integration_state_not_found(fixture_authorized_user):

    org = await OrganizationFactory(
        full_name="123",
        short_name="123"
    )
    dep = await DepartmentFactory(
        full_name="123",
        short_name="123",
        organization_id=org.id
    )
    user = await UserFactory(department_id=dep.id)
    json_ = {
        "state": IntegrationUserState.OK,
        "reason": "TEST"
    }

    response = await fixture_authorized_user.get("client").put(
        (
            f"{m_s.USE_PREFIX}/integrations/{JobSiteMacroEnum.HEADHUNTER.lower()}"
            f"/{user.id}/state"
        ),
        json=json_
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_user_with_job_site_policy(fixture_authorized_user):

    org = await OrganizationFactory(
        full_name="123",
        short_name="123"
    )
    dep = await DepartmentFactory(
        full_name="123",
        short_name="123",
        organization_id=org.id
    )
    user = await UserFactory(department_id=dep.id)
    await JobSitePolicyFactory(organization_id=org.id)

    response = await fixture_authorized_user.get("client").get(
        f"{m_s.USE_PREFIX}/integrations/policy/"
        f"{JobSiteMacroEnum.HEADHUNTER.lower()}/{user.id}",
    )

    assert response.status_code == status.HTTP_200_OK

    result = response.json()

    assert result["billing_type"]["name"] == OrganizationBillingType.FREE


@pytest.mark.asyncio
async def test_get_user_with_job_site_policy_not_found(fixture_authorized_user):

    org = await OrganizationFactory(
        full_name="123",
        short_name="123"
    )
    dep = await DepartmentFactory(
        full_name="123",
        short_name="123",
        organization_id=org.id
    )
    user = await UserFactory(department_id=dep.id)

    response = await fixture_authorized_user.get("client").get(
        f"{m_s.USE_PREFIX}/integrations/policy/"
        f"{JobSiteMacroEnum.HEADHUNTER.lower()}/{user.id}",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
