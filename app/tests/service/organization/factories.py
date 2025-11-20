import factory

from service.organizations.models import Department, Organization, JobSitePolicy
from service.types import JobSiteMacroEnum, OrganizationBillingType
from tests.common.factories import AsyncSQLAlchemyFactory, CommonMeta


class OrganizationFactory(AsyncSQLAlchemyFactory):

    class Meta(CommonMeta):
        model = Organization

    id = factory.Sequence(lambda n: n + 100)

    full_name = 'FACTORY_ORGANIZATION'
    short_name = 'FACTORY_ORGANIZATION'

    corp_email = factory.Faker('email')
    corp_phone = factory.Faker('phone_number')


class DepartmentFactory(AsyncSQLAlchemyFactory):

    class Meta(CommonMeta):
        model = Department

    id = factory.Sequence(lambda n: n + 100)
    organization_id = factory.Sequence(lambda n: n + 100)

    full_name = 'FACTORY_DEPARTMENT'
    short_name = 'FACTORY_DEPARTMENT'


class JobSitePolicyFactory(AsyncSQLAlchemyFactory):

    class Meta(CommonMeta):
        model = JobSitePolicy

    id = factory.Sequence(lambda n: n + 100)
    organization_id = None
    platform_type = JobSiteMacroEnum.HEADHUNTER
    billing_info = {
        "name": OrganizationBillingType.FREE
    }
