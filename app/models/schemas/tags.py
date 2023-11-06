from pydantic import BaseModel, field_validator

from app.utilities.validators.payload.text import validate_text


class TagBaseSchema(BaseModel):
    id: int
    title: str

    @field_validator("title")
    @classmethod
    def validate_tag_title(cls, value):
        return validate_text(value, "title")


class TagSchema(TagBaseSchema):
    description: str

    @field_validator("description")
    @classmethod
    def validate_tag_description(cls, value):
        return validate_text(value, "description")


# TODO: find out how to simplify
class TagCreateInput(BaseModel):
    title: str
    description: str
    company_id: int

    @field_validator("title")
    @classmethod
    def validate_tag_title(cls, value):
        return validate_text(value, "title")

    @field_validator("description")
    @classmethod
    def validate_tag_description(cls, value):
        return validate_text(value, "description")


class TagCreateOutput(BaseModel):
    tag_id: int
