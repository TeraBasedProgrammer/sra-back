from typing import Optional

from pydantic import BaseModel, Field, field_validator

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
    title: str = Field(min_length=4, max_length=30)
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


# TODO: find out how to simplify
class TagUpdateInput(BaseModel):
    title: Optional[str] = Field(min_length=4, max_length=30, default=None)
    description: Optional[str] = Field(default=None)
