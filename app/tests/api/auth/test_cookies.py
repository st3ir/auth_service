from datetime import datetime, timedelta

import pytest
from freezegun import freeze_time

from settings import auth_settings as a_s
from tests.constants import USER__WHOAMI_URL


@pytest.mark.skip
async def test_access_token_times_up(fixture_mock_redis, fixture_authorized_user):
    client = fixture_authorized_user.get("client")
    expected_cookie = client.cookies.get(
        a_s.COOKIE_SESSION_KEY
    )

    response = await client.get(
        USER__WHOAMI_URL
    )

    assert response.status_code == 200
    assert response.cookies.get(a_s.COOKIE_SESSION_KEY) == expected_cookie
    with (
        freeze_time(
            datetime.now()
            + timedelta(minutes=int(a_s.ACCESS_TOKEN_EXPIRES_MINUTES) + 10)
        )
    ):
        response = await client.get(
            USER__WHOAMI_URL
        )
        assert response.cookies.get(a_s.COOKIE_SESSION_KEY) != expected_cookie

    with freeze_time(datetime.now() + timedelta(weeks=100_500)):
        response = await client.get(
            USER__WHOAMI_URL
        )
        assert response.status_code == 401


@pytest.mark.skip
async def test_refresh_token_times_up(fixture_mock_redis, fixture_authorized_user):
    client = fixture_authorized_user.get("client")

    with freeze_time(datetime.now() + timedelta(weeks=100_500)):
        response = await client.get(
            USER__WHOAMI_URL
        )
        assert response.status_code == 401
