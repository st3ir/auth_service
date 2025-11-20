import json

from factory import DictFactory
from factory.alchemy import SQLAlchemyModelFactory

from tests.conftest import factory_session


class AsyncSQLAlchemyFactory(SQLAlchemyModelFactory):

    @classmethod
    async def create(cls, **kwargs) -> SQLAlchemyModelFactory:
        return await super().create(**kwargs)

    @classmethod
    async def create_batch(cls, size, **kwargs):
        return [await cls.create(**kwargs) for _ in range(size)]

    @classmethod
    async def _create(cls, model_class, *args, **kwargs):
        return await cls._save(model_class, *args, **kwargs)

    @classmethod
    async def _save(cls, model_class, *args, **kwargs):
        session = cls._meta.sqlalchemy_session
        obj = model_class(*args, **kwargs)

        session.add(obj)
        await session.commit()

        return obj

    @classmethod
    def model_dump(cls, obj) -> dict:

        return {
            column.name: getattr(obj, column.name)
            for column
            in obj.__table__.columns
        }

    class Meta:
        abstract = True


class CommonMeta:
    sqlalchemy_session = factory_session


class JsonFactory(DictFactory):

    @classmethod
    def _generate(cls, strategy, params) -> str:

        obj = super()._generate(strategy, params)
        return json.dumps(obj)
