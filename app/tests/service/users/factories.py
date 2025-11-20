import factory
from factory import faker, fuzzy

from service.helpers import utils
from service.types import JobSiteMacroEnum, UserAgreementType
from service.users.models import JobSiteCredentials, User, UserAgreement
from tests.common.factories import AsyncSQLAlchemyFactory, CommonMeta
from tests.constants import GLOBAL_PASSWORD, GLOBAL_PASSWORD_SALT


class UserFactory(AsyncSQLAlchemyFactory):

    class Meta(CommonMeta):
        model = User

    id = factory.Sequence(lambda n: n + 100)

    department_id = None

    first_name = fuzzy.FuzzyText(length=50)
    last_name = fuzzy.FuzzyText(length=50)
    parent_name = fuzzy.FuzzyText(length=50)

    pass_salt = GLOBAL_PASSWORD_SALT
    email = faker.Faker('email')
    active = True

    @factory.lazy_attribute
    def password(self) -> str:
        return utils.get_hash(
            GLOBAL_PASSWORD + GLOBAL_PASSWORD_SALT
        )


class JobSiteCredentialsFactory(AsyncSQLAlchemyFactory):

    class Meta(CommonMeta):
        model = JobSiteCredentials

    id = factory.Sequence(lambda n: n + 100)
    user_id = None
    credentials = {"access_token": "q"}
    platform_type = JobSiteMacroEnum.HEADHUNTER


class UserAgreementFactory(AsyncSQLAlchemyFactory):

    class Meta(CommonMeta):

        model = UserAgreement

    id = factory.Sequence(lambda n: n + 100)
    user_id = None
    organization_id = None
    agreement_type = UserAgreementType.EULA
