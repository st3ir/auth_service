import pytest

from settings import main_settings as m_s


@pytest.mark.asyncio
async def test_get_departments(fixture_authorized_user):

    organization = fixture_authorized_user.get("organization")
    department = fixture_authorized_user.get("department")
    client = fixture_authorized_user.get("client")

    params = {
        'organization_ids': [1, department.id, 3]
    }
    response = await client.get(
        f'{m_s.USE_PREFIX}/organizations/departments', params=params
    )

    assert response.status_code == 200

    content = response.json()
    content_by_org = content[organization.full_name]

    assert len(content_by_org) == 1
    assert content_by_org[0]['id'] == department.id


@pytest.mark.asyncio
async def test_get_departments_not_found(fixture_authorized_user):
    client = fixture_authorized_user.get("client")

    params = {
        'organization_ids': [1, 2, 3]
    }
    response = await client.get(
        f'{m_s.USE_PREFIX}/organizations/departments', params=params
    )

    assert response.status_code == 200

    content = response.json()

    assert len(content.keys()) == 0


@pytest.mark.asyncio
async def test_get_departments_by_search_name(fixture_authorized_user):

    organization = fixture_authorized_user.get("organization")
    department = fixture_authorized_user.get("department")
    client = fixture_authorized_user.get("client")

    params = {
        'organization_ids': [1, department.id, 3],
        'department_name': department.full_name.upper()
    }
    response = await client.get(
        f'{m_s.USE_PREFIX}/organizations/departments', params=params
    )

    assert response.status_code == 200

    content = response.json()
    content_by_org = content[organization.full_name]

    assert len(content_by_org) == 1
    assert content_by_org[0]['id'] == department.id


@pytest.mark.asyncio
async def test_get_departments_by_search_name_empty(fixture_authorized_user):

    department = fixture_authorized_user.get("department")
    client = fixture_authorized_user.get("client")

    params = {
        'organization_ids': [1, department.id, 3],
        'department_name': str(department.id)
    }
    response = await client.get(
        f'{m_s.USE_PREFIX}/organizations/departments', params=params
    )

    assert response.status_code == 200

    content = response.json()
    assert len(content) == 0


@pytest.mark.asyncio
async def test_get_department_by_id(fixture_authorized_user):
    department = fixture_authorized_user.get("department")
    client = fixture_authorized_user.get("client")

    response = await client.get(
        f'{m_s.USE_PREFIX}/organizations/departments/{department.id}',
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_department_by_id_not_found(fixture_client):
    response = await fixture_client.get(
        f'/api/organizations/departments/{1}'
    )

    assert response.status_code == 404
