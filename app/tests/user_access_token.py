from settings import auth_settings as a_s

from service.helpers import utils


async def get_user_access_token(new_user, role):
    ACCESS_TOKEN = utils.create_token(
        {
            "email": new_user.email,
            "user_id": new_user.id,
            "role": role.rolename,
        },
        minutes=int(a_s.ACCESS_TOKEN_EXPIRES_MINUTES),
        secret_key=a_s.ACCESS_TOKEN_SECRET_KEY,
        algorithm=a_s.TOKENS_ALGORITHM,
    )
    REFRESH_TOKEN = utils.create_token(
        {
            "email": new_user.email,
        },
        minutes=int(a_s.REFRESH_TOKEN_EXPIRES_MINUTES),
        secret_key=a_s.REFRESH_TOKEN_SECRET_KEY,
        algorithm=a_s.TOKENS_ALGORITHM,
    )

    return ACCESS_TOKEN, REFRESH_TOKEN
