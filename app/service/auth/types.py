from typing import TypeAlias, TypedDict

AccessToken: TypeAlias = str
RefreshToken: TypeAlias = str


class BaseTokenTD(TypedDict):
    email: str


class AccessTokenTD(BaseTokenTD):
    user_id: str
    role: str


class RefreshTokenTD(BaseTokenTD):
    pass
