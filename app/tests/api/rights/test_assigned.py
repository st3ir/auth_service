import pytest
from fastapi import status

from settings import main_settings as m_s
from service.rights.types import HiddenFieldsVacancy, RightType, SourceType
from tests.service.rights.factories import SpecRightsFactory, UserRightsFactory


@pytest.mark.asyncio
async def test_vacancy_assigned(fixture_authorized_user):

    admin_user = fixture_authorized_user.get("user")
    client = fixture_authorized_user.get("client")

    source_id = 1
    right = await SpecRightsFactory(
        source_type=SourceType.VACANCY,
        right_type=RightType.VIEW_PUBLIC,
        source_id=source_id,
    )
    await UserRightsFactory(
        subject_id=admin_user.id,
        right_id=right.id,
        constraints={
            "hidden_fields": [
                HiddenFieldsVacancy.SALARY_FROM,
                HiddenFieldsVacancy.SALARY_TO
            ]
        }
    )
    params = {
        "source_type": SourceType.VACANCY
    }
    response = await client.get(
        f'{m_s.USE_PREFIX}/rights/by-rel/{source_id}',
        params=params,
    )

    assert response.status_code == status.HTTP_200_OK

    response = response.json()
    assert len(response[RightType.VIEW_PUBLIC]) == 1

    right_user = response[RightType.VIEW_PUBLIC][0]
    assert len(right_user["constraints"]["hidden_fields"]) == 2
