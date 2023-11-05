from pydantic import BaseModel, field_validator

from app.utilities.validators.text import validate_text


class TagBaseSchema(BaseModel):
    title: str
    description: str

    @field_validator("title")
    @classmethod
    def validate_tag_title(cls, value):
        return validate_text(value, "title")

    @field_validator("description")
    @classmethod
    def validate_tag_description(cls, value):
        return validate_text(value, "description")


class TagSchema(TagBaseSchema):
    id: int
    company_id: int
