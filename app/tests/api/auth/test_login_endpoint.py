import pytest
from factory import faker

from settings import auth_settings as a_s
from tests.constants import AUTH__LOGIN_URL, GLOBAL_PASSWORD


@pytest.mark.asyncio
async def test_login_inactive_user(
    fixture_inactive_user, fixture_client
):
    response = await fixture_client.post(
        AUTH__LOGIN_URL,
        data={
            "username": fixture_inactive_user.get("user").email,
            "password": GLOBAL_PASSWORD,
        },
    )
    assert response.status_code == 401
    assert response.cookies.get(a_s.COOKIE_SESSION_KEY) is None


@pytest.mark.asyncio
async def test_login_undefined_user(
    fixture_client
):
    response = await fixture_client.post(
        AUTH__LOGIN_URL,
        data={
            "username": faker.Faker('email'),
            "password": GLOBAL_PASSWORD,
        },
    )
    assert response.status_code == 401
    assert response.cookies.get(a_s.COOKIE_SESSION_KEY) is None
