from fastapi import Form
from pydantic import BaseModel, field_validator
from pydantic.v1 import ConfigDict

from service.roles.models import Role
from service.roles.types import RoleType


class UserBase(BaseModel):

    id: int
    email: str


class UserCreate(BaseModel):

    department_id: int | None = None

    email: str
    password: str
    active: bool = False

    first_name: str
    last_name: str
    parent_name: str | None = None

    @classmethod
    def as_form(
        cls,
        email: str = Form(),
        department_id: int | None = Form(None),
        password: str = Form(),
        active: bool = Form(False),
        first_name: str = Form(),
        last_name: str = Form(),
        parent_name: str | None = Form(None)
    ):
        return cls(
            department_id=department_id,
            email=email,
            password=password,
            active=active,
            first_name=first_name,
            last_name=last_name,
            parent_name=parent_name
        )


class UserUpdateSchema(BaseModel):
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    parent_name: str | None = None

    @classmethod
    def as_form(
        cls,
        email: str | None = Form(None),
        first_name: str | None = Form(None),
        last_name: str | None = Form(None),
        parent_name: str | None = Form(None),
    ):
        return cls(
            email=email,
            first_name=first_name,
            last_name=last_name,
            parent_name=parent_name
        )


class User(UserBase):

    active: bool
    first_name: str
    last_name: str
    role: str
    photo_link: str | None

    @field_validator("role", mode='before')
    def get_role_from_model(cls, role: Role) -> str:
        return role.rolename


class RoleBase(BaseModel):

    rolename: str


class RoleCreate(RoleBase):
    pass


class RoleSchema(RoleBase):

    id: int
    users: list["UserRoleAssociation"]


class UserRoleAssociationBase(BaseModel):
    pass


class UserRoleAssociationCreate(UserRoleAssociationBase):
    user_id: int
    role_id: int


class UserRoleAssociation(UserRoleAssociationBase):
    id: int
    user: User
    role: RoleSchema

    model_config = ConfigDict(with_attributes=True)


class UserTTBase(UserBase):

    first_name: str
    last_name: str
    parent_name: str | None = None
    photo_link: str | None = None
    role: RoleType | None = None
    is_eula_accepted: bool | None = None

    @field_validator("role", mode='before')
    def get_role_from_model(cls, role: Role | str) -> str:
        if isinstance(role, str):
            return role
        return role.rolename


class UserTTInfo(UserTTBase):

    active: bool
    department_id: int | None = None
    organization_id: int | None = None
    phone_number: str | None = None

    is_internal: bool


class UserTTInfoPhone(UserTTBase):

    phone_number: str | None = None
    department_id: int | None = None
    organization_id: int | None = None

    is_internal: bool


class UserFullInfo(UserTTBase):
    corp_phone: str
    organization_name: str


class UserRoleVerify(BaseModel):
    role: str | None = None


class UserVerifyInfo(BaseModel):

    id: int
    first_name: str
    last_name: str
    parent_name: str | None = None

    photo_link: str | None = None
    role: RoleType
    department_id: int | None = None
    organization_id: int | None = None


class UserInfoWithAssign(UserTTBase):

    is_assigned: bool | None = False
