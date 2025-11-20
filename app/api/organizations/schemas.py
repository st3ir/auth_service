from pydantic import BaseModel, RootModel


class ShortDepartmentSchema(BaseModel):

    id: int
    full_name: str
    organization_name: str


class DetailDepartmentSchema(BaseModel):

    id: int
    organization_id: int
    full_name: str
    short_name: str


class DepartmentWithOrgSchema(RootModel):

    root: dict[str, list[ShortDepartmentSchema] | None]


class DepartmentByIntegrationSchema(BaseModel):

    id: int
    external_id: str


class DepartmentWithExternalSchema(RootModel):

    root: dict[str, int] | None = None
