from pydantic import BaseModel, HttpUrl, model_validator

from service.rights.types import HiddenFieldsVacancy, RightType, SourceType


class RightSchemaTypes(BaseModel):

    source_type: SourceType
    right_type: RightType


class ConstraintsSchema(BaseModel):

    hidden_fields: list[HiddenFieldsVacancy] | None = []


class RightSchemaTypesWithConstraints(RightSchemaTypes):

    constraints: ConstraintsSchema | None = ConstraintsSchema()

    @model_validator(mode="after")
    def validate_hidden_fields(self):

        if (
            (
                self.right_type != RightType.VIEW_PUBLIC
                or self.source_type != SourceType.VACANCY
            )
            and self.constraints.hidden_fields
        ):
            raise ValueError("Hidden fields only for VIEW_PUBLIC and VACANCY")

        return self


class RightSchemaBase(RightSchemaTypesWithConstraints):

    source_id: int


class GrantRightSchema(RightSchemaTypes):
    pass


class RightSchema(RightSchemaBase):

    subject_id: int


class GrantRightToUsersSchema(RightSchemaTypesWithConstraints):

    user_ids_in: list[int] | None = []
    user_ids_out: list[int] | None = []


class UserWithGrantSchema(BaseModel):

    subject_id: int
    first_name: str
    last_name: str
    parent_name: str | None = None
    photo_link: HttpUrl | None = None
    constraints: ConstraintsSchema | None = ConstraintsSchema()


class GroupedUsersWithGrantsSchema(BaseModel):

    VIEW_ALL: list[UserWithGrantSchema] | None = []
    VIEW_PUBLIC: list[UserWithGrantSchema] | None = []
    MANAGE: list[UserWithGrantSchema] | None = []


class RightsChangedSchema(BaseModel):

    is_changed: bool


class GrantedSourcesByType(BaseModel):

    MANAGE: list[int] | None = []
    VIEW_ALL: list[int] | None = []
    VIEW_PUBLIC: list[int] | None = []


class GrantedSourcesSchema(BaseModel):

    assigned_source_ids: list[int] | None = []
    grouped: GrantedSourcesByType
