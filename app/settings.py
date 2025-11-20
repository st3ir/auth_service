from dotenv import load_dotenv
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings


load_dotenv(override=True)


class Settings(BaseSettings):

    CORS_ORIGINS: list[str] = [
        'http://localhost',
        'http://localho.st',
        'https://localhost',
        'http://scoutzone.ru',
        'https://scoutzone.ru',
        'http://localhost:80',
        'http://localhost:3000',
        'http://localhost:8000',
        'https://localhost:8000',
        'http://localhost:4173',
        'http://localhost:5173',
    ]
    USE_PREFIX: str = Field(
        '/api',
        alias='USE_PREFIX'
    )

    SERVICE_USER_EMAIL: str | None = Field(
        None,
        alias='SERVICE_USER_EMAIL'
    )

    SERVICE_USER_PASS: str | None = Field(
        None,
        alias='SERVICE_USER_PASS'
    )


class PostgresSettings(BaseSettings):

    POSTGRES_DB: str | None = Field(None)
    POSTGRES_USER: str | None = Field(None)
    POSTGRES_PASSWORD: str | None = Field(None)
    POSTGRES_HOST: str | None = Field(None)

    @property
    def DATABASE_URL(self) -> str:
        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            path=f'{self.POSTGRES_DB or ""}',
        ).unicode_string()


class TestPostgresSettings(BaseSettings):

    POSTGRES_DB: str | None = Field(None, alias='TEST_POSTGRES_DB')
    POSTGRES_USER: str | None = Field(None, alias='TEST_POSTGRES_USER')
    POSTGRES_PASSWORD: str | None = Field(None, alias='TEST_POSTGRES_PASSWORD')
    POSTGRES_HOST: str | None = Field(None, alias='TEST_POSTGRES_HOST')

    @property
    def TEST_DATABASE_URL(self) -> str:

        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            path=f'{self.POSTGRES_DB or ""}',
        ).unicode_string()


class AuthSettings(BaseSettings):

    ACCESS_TOKEN_SECRET_KEY: str | None = Field(
        None, alias='ACCESS_TOKEN_SECRET_KEY'
    )
    REFRESH_TOKEN_SECRET_KEY: str | None = Field(
        None,
        alias='REFRESH_TOKEN_SECRET_KEY'
    )
    ACCESS_TOKEN_EXPIRES_MINUTES: str | None = Field(
        None,
        alias='ACCESS_TOKEN_EXPIRES_MINUTES'
    )
    REFRESH_TOKEN_EXPIRES_MINUTES: str | None = Field(
        None,
        alias='REFRESH_TOKEN_EXPIRES_MINUTES'
    )
    POSTGRES_DB: str | None = Field(None, alias='TEST_POSTGRES_DB')

    TOKENS_ALGORITHM: str = "HS256"
    COOKIE_SESSION_KEY: str = Field('X-AUTH', alias='COOKIE_SESSION_KEY')

    SKIP_AUTH: int = Field(0, alias='SKIP_AUTH')
    SKIP_AGREEMENT: int = Field(
        0,
        alias='HR_SKIP_AGREEMENT'
    )


class RedisSettings(BaseSettings):

    REDIS_URL: str | None = Field(None, alias='REDIS_URL')


main_settings = Settings()


class S3Settings(BaseSettings):

    BUCKET_URL: str | None = Field(None, alias='HR_BUCKET_URL')
    BUCKET_ACCESS_KEY: str | None = Field(None, alias='HR_BUCKET_ACCESS_KEY')
    BUCKET_SECRET_KEY: str | None = Field(None, alias='HR_BUCKET_SECRET_KEY')
    BUCKET_REGION: str | None = Field(None, alias='HR_BUCKET_REGION')
    BUCKET_NAME: str | None = Field(None, alias='HR_BUCKET_NAME')

    S3_PROXY_URL: str | None = Field('localhost', alias='HR_S3_PROXY_URL')
    S3_IMAGES_PATH: str = Field('images', alias='HR_BUCKET_S3_IMAGES_PATH')

    DOMAIN_URL: str = Field('localhost', alias='HR_DOMAIN_URL')

    MAX_IMAGE_SIZE: int = 10000000

    ALLOWED_IMAGE_TYPES: list[str] = [
        "image/png",
        "image/jpeg",
        "image/jpg",
        "image/webp"
        "png",
        "jpeg",
        "jpg",
        "webp"
    ]

    @property
    def USER_STATIC_IMG_URL(self) -> str:
        return self.DOMAIN_URL + main_settings.USE_PREFIX + "/static/user-img/"

    @property
    def DEFAULT_STATIC_IMG_URL(self) -> str:
        return self.USER_STATIC_IMG_URL + 'default.png'


auth_settings = AuthSettings()
redis_settings = RedisSettings()
s3_settings = S3Settings()
postgres_settings = PostgresSettings()
test_postgres_settings = PostgresSettings()
