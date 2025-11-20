import pytest
from fastapi import status
from httpx import Response

from service.rights.types import HiddenFieldsVacancy, RightType, SourceType
from settings import main_settings as m_s
from tests.service.rights.factories import SpecRightsFactory, UserRightsFactory


@pytest.mark.asyncio
async def test_add_empty_contraints_with_rights(fixture_authorized_user):

    client = fixture_authorized_user.get("client")
    user_id = fixture_authorized_user['user'].id
    source_id = 1

    data = {
        "user_ids_in": [user_id],
        'user_ids_out': [],
        'right_type': RightType.VIEW_ALL,
        "source_type": SourceType.VACANCY,
        "constraints": {"hidden_fields": []}
    }

    params = {
        "by_nested": True,
    }

    response: Response = await client.put(
        f'{m_s.USE_PREFIX}/rights/by-rel/{source_id}',
        json=data,
        params=params,
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_add_contraints_with_rights(fixture_authorized_hr_employee_user):

    client = fixture_authorized_hr_employee_user.get("client")
    user_id = fixture_authorized_hr_employee_user['user'].id
    source_id = 1

    data = {
        "user_ids_in": [user_id],
        'user_ids_out': [],
        'right_type': RightType.VIEW_PUBLIC,
        "source_type": SourceType.VACANCY,
        "constraints": {
            "hidden_fields": [
                HiddenFieldsVacancy.SALARY_TO,
                HiddenFieldsVacancy.SALARY_FROM
            ]
        }
    }

    params = {
        "by_nested": True,
    }

    response: Response = await client.put(
        f'{m_s.USE_PREFIX}/rights/by-rel/{source_id}',
        json=data,
        params=params,
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_contraints_with_rights(fixture_authorized_hr_employee_user):

    user = fixture_authorized_hr_employee_user.get("user")
    client = fixture_authorized_hr_employee_user.get("client")

    source_id = 1
    spec = await SpecRightsFactory(
        source_type=SourceType.VACANCY,
        source_id=source_id,
        right_type=RightType.VIEW_PUBLIC
    )

    await UserRightsFactory(
        subject_id=user.id,
        right_id=spec.id,
        constraints={
            "hidden_fields": [
                HiddenFieldsVacancy.SALARY_TO,
                HiddenFieldsVacancy.SALARY_FROM
            ]
        }
    )

    response: Response = await client.get(
        f'{m_s.USE_PREFIX}/rights/by-rel/{source_id}/{user.id}',
        params={
            "source_type": SourceType.VACANCY,
        },
    )

    assert response.status_code == 200
    response = response.json()

    assert len(response["constraints"]["hidden_fields"]) == 2


@pytest.mark.asyncio
async def test_add_contraints_with_broken_rights_1(fixture_authorized_user):

    client = fixture_authorized_user.get("client")
    user_id = fixture_authorized_user['user'].id
    source_id = 1

    data = {
        "user_ids_in": [user_id],
        'user_ids_out': [],
        'right_type': RightType.MANAGE,
        "source_type": SourceType.VACANCY,
        "constraints": {
            "hidden_fields": [
                HiddenFieldsVacancy.SALARY_TO,
                HiddenFieldsVacancy.SALARY_FROM
            ]
        }
    }

    params = {
        "by_nested": True,
    }

    response: Response = await client.put(
        f'{m_s.USE_PREFIX}/rights/by-rel/{source_id}',
        json=data,
        params=params,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_add_contraints_with_broken_rights_2(fixture_authorized_user):

    client = fixture_authorized_user.get("client")
    user_id = fixture_authorized_user['user'].id
    source_id = 1

    data = {
        "user_ids_in": [user_id],
        'user_ids_out': [],
        'right_type': RightType.DELETE,
        "source_type": SourceType.RESUME,
        "constraints": {
            "hidden_fields": [
                HiddenFieldsVacancy.SALARY_TO,
                HiddenFieldsVacancy.SALARY_FROM
            ]
        }
    }

    params = {
        "by_nested": True,
    }

    response: Response = await client.put(
        f'{m_s.USE_PREFIX}/rights/by-rel/{source_id}',
        json=data,
        params=params,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_add_invalid_rights_for_user(fixture_authorized_user):

    client = fixture_authorized_user.get("client")
    user_id = fixture_authorized_user['user'].id
    source_id = 1

    data = {
        "user_ids_in": [user_id],
        'user_ids_out': [],
        'right_type': RightType.VIEW_PUBLIC,
        "source_type": SourceType.VACANCY,
        "constraints": {
            "hidden_fields": [
                HiddenFieldsVacancy.SALARY_TO,
                HiddenFieldsVacancy.SALARY_FROM
            ]
        }
    }

    params = {
        "by_nested": True,
    }

    response: Response = await client.put(
        f'{m_s.USE_PREFIX}/rights/by-rel/{source_id}',
        json=data,
        params=params,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_add_invalid_rights_for_user_2(fixture_authorized_hr_employee_user):

    client = fixture_authorized_hr_employee_user.get("client")
    user_id = fixture_authorized_hr_employee_user['user'].id
    source_id = 1

    data = {
        "user_ids_in": [user_id],
        'user_ids_out': [],
        'right_type': RightType.DELETE,
        "source_type": SourceType.VACANCY,
    }

    params = {
        "by_nested": True,
    }

    response: Response = await client.put(
        f'{m_s.USE_PREFIX}/rights/by-rel/{source_id}',
        json=data,
        params=params,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_add_invalid_rights_for_users(
    fixture_authorized_hr_employee_user,
    fixture_authorized_user
):

    client = fixture_authorized_hr_employee_user.get("client")
    hr_employee_user_id = fixture_authorized_hr_employee_user['user'].id
    hr_recruiter_user_id = fixture_authorized_user['user'].id

    source_id = 1

    data = {
        "user_ids_in": [hr_employee_user_id, hr_recruiter_user_id],
        'user_ids_out': [],
        'right_type': RightType.VIEW_PUBLIC,
        "source_type": SourceType.VACANCY,
    }

    params = {
        "by_nested": True,
    }

    response: Response = await client.put(
        f'{m_s.USE_PREFIX}/rights/by-rel/{source_id}',
        json=data,
        params=params,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
