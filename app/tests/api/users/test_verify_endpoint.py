import pytest

from settings import auth_settings as a_s
from service.helpers import utils
from tests.constants import USER__VERIFY_URL


@pytest.mark.asyncio
async def test_without_header(
    fixture_client
):
    response = await fixture_client.get(USER__VERIFY_URL)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_with_active_user_in_header(
    fixture_authorized_user
):
    user = fixture_authorized_user.get("user")
    response = await fixture_authorized_user.get("client").get(
        USER__VERIFY_URL
    )

    assert response.status_code == 200

    info = response.json()
    assert info['id'] == user.id
    assert info['role'] == fixture_authorized_user.get("role").rolename
    assert info['department_id'] == user.department_id


@pytest.mark.asyncio
async def test_with_fake_role_in_header(
    fixture_client, fixture_user
):
    fake_cookie = utils.create_token(
        {
            "email": fixture_user.get("user").email,
            "user_id": fixture_user.get("user").id,
            "role": "PEPE",
        },
        minutes=int(a_s.ACCESS_TOKEN_EXPIRES_MINUTES),
        secret_key=a_s.ACCESS_TOKEN_SECRET_KEY,
        algorithm=a_s.TOKENS_ALGORITHM,
    )
    response = await fixture_client.get(
        USER__VERIFY_URL,
        headers={"Authorization": f'Bearer {fake_cookie}'}
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_with_fake_email_in_header(
    fixture_client, fixture_user
):
    fake_cookie = utils.create_token(
        {
            "email": "test_email",
            "user_id": fixture_user.get("user").id,
            "role": fixture_user.get("role").rolename,
        },
        minutes=int(a_s.ACCESS_TOKEN_EXPIRES_MINUTES),
        secret_key=a_s.ACCESS_TOKEN_SECRET_KEY,
        algorithm=a_s.TOKENS_ALGORITHM,
    )

    response = await fixture_client.get(
        USER__VERIFY_URL,
        headers={"Authorization": f'Bearer {fake_cookie}'}
    )

    assert response.status_code == 401
