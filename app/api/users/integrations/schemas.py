from datetime import datetime

from pydantic import BaseModel, RootModel

from service.types import (
    IntegrationUserState,
    JobSiteMacroEnum,
    OrganizationBillingType
)


class BaseIntegrationUserStateSchema(BaseModel):

    state: IntegrationUserState = IntegrationUserState.OK
    reason: str | None = None


class UserIntagrationStateSchema(BaseIntegrationUserStateSchema):

    is_success: bool


class UserIntegrationStatesSchema(RootModel):

    root: dict[JobSiteMacroEnum, UserIntagrationStateSchema]


class HHCredentials(BaseModel):

    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

    user_state: BaseIntegrationUserStateSchema

    updated_at: datetime
    created_at: datetime


class AppUserCredentials(BaseModel):

    user_id: int | None = None
    platform_type: JobSiteMacroEnum | None = None
    credentials: HHCredentials


class HHBillingSchema(BaseModel):
    name: OrganizationBillingType


class ServiceUserJobSitePolicy(BaseModel):

    organization_id: int | None = None
    platform_type: JobSiteMacroEnum | None = None
    billing_type: HHBillingSchema


class UserWithCredsSchema(BaseModel):

    user_id: int
    is_priority: bool


class UsersWithCredsSchema(RootModel):

    root: list[UserWithCredsSchema] | None = []
