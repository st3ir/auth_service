import pytest
from sqlalchemy import select

from service.rights.types import RightType, SourceType
from service.roles.models import Role
from service.roles.types import RoleType
from settings import main_settings as m_s
from tests.conftest import async_session
from tests.service.rights.factories import SpecRightsFactory, UserRightsFactory
from tests.service.roles.factories import UserRoleFactory
from tests.service.users.factories import UserFactory


@pytest.mark.asyncio
async def test_get_users_rights_by_source_id(fixture_authorized_user):

    user = fixture_authorized_user.get("user")
    department = fixture_authorized_user.get("department")
    client = fixture_authorized_user.get("client")

    source_id = 1

    for _ in range(10):
        right = await SpecRightsFactory(
            source_type=SourceType.VACANCY, source_id=source_id
        )
        new_user = await UserFactory(department_id=department.id)
        await UserRightsFactory(subject_id=new_user.id, right_id=right.id)

    new_right = await SpecRightsFactory(
        source_type=SourceType.VACANCY, right_type=RightType.MANAGE,
        source_id=source_id
    )

    await UserRightsFactory(subject_id=user.id, right_id=new_right.id)

    params = {
        "source_type": SourceType.VACANCY,
    }

    response = await client.get(
        f'{m_s.USE_PREFIX}/rights/by-rel/{source_id}',
        params=params,
    )

    assert response.status_code == 200

    content = response.json()

    assert content[RightType.MANAGE]


@pytest.mark.asyncio
async def test_get_user_rights_filtered(fixture_authorized_user):

    user = fixture_authorized_user.get("user")
    client = fixture_authorized_user.get("client")

    right = await SpecRightsFactory(
        source_type=SourceType.VACANCY_REQUEST, right_type=RightType.MANAGE
    )

    await UserRightsFactory(subject_id=user.id, right_id=right.id)

    params = {
        "source_type": SourceType.VACANCY_REQUEST,
        "right_type": RightType.MANAGE
    }

    response = await client.get(
        f'{m_s.USE_PREFIX}/rights/by-rel/{right.source_id}',
        params=params,
    )

    assert response.status_code == 200

    content = response.json()

    assert len(content[RightType.MANAGE]) == 1
    assert not content[RightType.VIEW_ALL]
    assert not content[RightType.VIEW_PUBLIC]


@pytest.mark.asyncio
async def test_set_user_right(fixture_authorized_user):

    admin_user = fixture_authorized_user.get("user")
    department = fixture_authorized_user.get("department")
    client = fixture_authorized_user.get("client")

    source_id = 1

    right = await SpecRightsFactory(
        source_type=SourceType.VACANCY, right_type=RightType.MANAGE,
        source_id=source_id
    )

    await UserRightsFactory(subject_id=admin_user.id, right_id=right.id)

    user = await UserFactory(department_id=department.id)
    async with async_session() as session:
        role = (
            await session.execute(
                select(Role).where(Role.rolename == RoleType.HR_RECRUITER)
            )
        ).scalar()
    await UserRoleFactory(user_id=user.id, role_id=role.id)

    right = await SpecRightsFactory(
        source_type=SourceType.VACANCY, source_id=source_id,
        right_type=RightType.VIEW_ALL,
    )
    await UserRightsFactory(subject_id=user.id, right_id=right.id)
    data = {
        "user_ids_in": [user.id],
        'user_ids_out': [],
        'right_type': RightType.VIEW_ALL,
        "source_type": SourceType.VACANCY
    }

    response = await client.put(
        f'{m_s.USE_PREFIX}/rights/by-rel/{source_id}',
        json=data,
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_remove_user_right_exception(fixture_authorized_user):

    admin_user = fixture_authorized_user.get("user")
    department = fixture_authorized_user.get("department")
    client = fixture_authorized_user.get("client")

    source_id = 1

    right = await SpecRightsFactory(
        source_type=SourceType.VACANCY, right_type=RightType.MANAGE,
        source_id=source_id
    )

    await UserRightsFactory(subject_id=admin_user.id, right_id=right.id)

    user = await UserFactory(department_id=department.id)

    right = await SpecRightsFactory(
        source_type=SourceType.VACANCY, source_id=source_id,
        right_type=RightType.VIEW_ALL,
    )
    await UserRightsFactory(subject_id=user.id, right_id=right.id)
    data = {
        "user_ids_in": [],
        'user_ids_out': [user.id],
        'right_type': RightType.VIEW_ALL,
        "source_type": SourceType.VACANCY
    }

    response = await client.put(
        f'{m_s.USE_PREFIX}/rights/by-rel/{source_id}',
        json=data,
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_rights_by_user(fixture_authorized_user):

    client = fixture_authorized_user.get("client")
    user_id = fixture_authorized_user['user'].id

    spec_rights_vacancy = await SpecRightsFactory(
        source_id=1,
        source_type=SourceType.VACANCY
    )
    spec_rights_vacancy_req = await SpecRightsFactory(
        source_id=1,
        source_type=SourceType.VACANCY_REQUEST
    )

    await UserRightsFactory(subject_id=user_id, right_id=spec_rights_vacancy.id)
    await UserRightsFactory(subject_id=user_id, right_id=spec_rights_vacancy_req.id)

    params = {
        'source_type': spec_rights_vacancy.source_type,
    }
    response = await client.get(
        f'{m_s.USE_PREFIX}/rights/by-user/{user_id}', params=params
    )

    assert response.status_code == 200

    content = response.json()
    assert len(content['assigned_source_ids']) == 1


@pytest.mark.asyncio
async def test_get_rights_by_user_with_params(fixture_authorized_user):

    client = fixture_authorized_user.get("client")
    user_id = fixture_authorized_user['user'].id

    spec_rights_manage = await SpecRightsFactory(
        source_id=1,
        source_type=SourceType.VACANCY,
        right_type=RightType.MANAGE
    )
    spec_rights_view_all = await SpecRightsFactory(
        source_id=2,
        source_type=SourceType.VACANCY,
        right_type=RightType.VIEW_ALL
    )

    await UserRightsFactory(subject_id=user_id, right_id=spec_rights_manage.id)
    await UserRightsFactory(subject_id=user_id, right_id=spec_rights_view_all.id)

    params = {
        'source_type': spec_rights_manage.source_type
    }
    response = await client.get(
        f'{m_s.USE_PREFIX}/rights/by-user/{user_id}', params=params
    )

    assert response.status_code == 200

    content = response.json()

    assert len(content['assigned_source_ids']) == 2
    assert len(content['grouped']['MANAGE']) == 1


@pytest.mark.asyncio
async def test_get_users_single_right_by_source_id(fixture_authorized_user):

    user = fixture_authorized_user.get("user")
    client = fixture_authorized_user.get("client")

    source_id = 1
    rights = [
        await SpecRightsFactory(
            source_type=SourceType.VACANCY,
            source_id=source_id,
            right_type=rt
        ) for rt in [RightType.VIEW_ALL, RightType.MANAGE, RightType.DELETE]
    ]

    for right in rights:
        await UserRightsFactory(subject_id=user.id, right_id=right.id)

    params = {
        "source_type": SourceType.VACANCY,
    }

    response = await client.get(
        f'{m_s.USE_PREFIX}/rights/by-rel/{source_id}/{user.id}',
        params=params,
    )

    assert response.status_code == 200

    content = response.json()
    assert content['right_type'] == RightType.DELETE
