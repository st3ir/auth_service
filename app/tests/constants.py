import uuid

from settings import main_settings as m_s

GLOBAL_PASSWORD = str(uuid.uuid4())
GLOBAL_PASSWORD_SALT = uuid.uuid4().hex

USER__VERIFY_URL = f"{m_s.USE_PREFIX}/users/verify"
USER__CREATE_USER_URL = f"{m_s.USE_PREFIX}/users"
USER__WHOAMI_URL = f"{m_s.USE_PREFIX}/users/whoami"

AUTH__LOGIN_URL = f"{m_s.USE_PREFIX}/auth"
AUTH__LOGOUT_URL = f"{m_s.USE_PREFIX}/logout"

AGREEMENTS__ACCEPT_URL = f"{m_s.USE_PREFIX}/agreements/accept"
