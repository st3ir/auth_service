import pytest

from settings import auth_settings as a_s
from tests.constants import AUTH__LOGIN_URL, GLOBAL_PASSWORD


@pytest.mark.skip
async def test_login_active_user(
    fixture_mock_redis, fixture_client, fixture_user
):

    response = await fixture_client.post(
        AUTH__LOGIN_URL,
        data={
            "username": fixture_user.get("user").email,
            "password": GLOBAL_PASSWORD,
        },
    )
    assert response.status_code == 200
    assert response.cookies.get(a_s.COOKIE_SESSION_KEY) is not None

    content = response.json()

    assert content["department_id"] == fixture_user.get("user").department_id
