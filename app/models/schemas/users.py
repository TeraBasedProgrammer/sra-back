from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, Extra, Field, field_validator

from app.models.schemas.tags import TagSchema
from app.utilities.validators.user import (
    validate_name,
    validate_password,
    validate_phone_number,
)


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = Field(max_length=50, min_length=2, default=None)
    phone_number: Optional[str] = Field(
        min_length=10, max_length=20, examples=["+380500505050"], default=None
    )

    @field_validator("name")
    @classmethod
    def validate_user_name(cls, value):
        return validate_name(value)

    @field_validator("phone_number")
    @classmethod
    def validate_user_phone_number(cls, value):
        return validate_phone_number(value)


class UserSchema(UserBase):
    id: int
    registered_at: datetime

    # Comment until bugs occur
    # role: Optional[RoleEnum] = Field(None, nullable=True)
    average_score: Decimal
    tags: list[TagSchema]

    class Config:
        from_attributes = True
        populate_by_name = True


class UserCreate(UserBase):
    auth0_registered: bool = Field(default=False)
    companies: list = Field(default=[])
    password: str


# TODO: figure out how to simplify
class UserUpdate(BaseModel):
    name: Optional[str] = Field(max_length=50, min_length=2, default=None)
    phone_number: Optional[str] = Field(
        min_length=10, max_length=20, examples=["+380500505050"], default=None
    )

    @field_validator("name")
    @classmethod
    def validate_user_name(cls, value):
        return validate_name(value)

    @field_validator("phone_number")
    @classmethod
    def validate_user_phone_number(cls, value):
        return validate_phone_number(value)

    class Config:
        extra = Extra.forbid


class PasswordResetInput(BaseModel):
    old_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate(cls, value: str):
        return validate_password(value)


class PasswordResetOutput(BaseModel):
    success: str = "The password was successfully reset"


class DeletedInstanceResponse(BaseModel):
    deleted_instance_id: int


class UpdateUserScore(BaseModel):
    overall_avg_score: Decimal
