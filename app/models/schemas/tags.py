from pydantic import BaseModel, field_validator

from app.utilities.validators.text import validate_text


class TagBaseSchema(BaseModel):
    title: str

    @field_validator("title")
    def validate_company_title(cls, value):
        return validate_text(value)


class TagSchema(TagBaseSchema):
    id: int
