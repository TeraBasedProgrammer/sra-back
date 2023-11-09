from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, Extra, Field, field_validator

from app.models.schemas.tags import TagBaseSchema
from app.utilities.validators.payload.user import (
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


class CompanyMemberInput(UserBase):
    password: str
    role: str
    tags: list[int]

    @field_validator("password")
    @classmethod
    def validate(cls, value: str):
        return validate_password(value)


class CompanyMemberUpdate(BaseModel):
    role: Optional[str] = None
    tags: Optional[list[int]] = None


class UserSchema(UserBase):
    id: int
    registered_at: datetime
    average_score: Decimal
    tags: list[TagBaseSchema]

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


class NewPasswordInput(BaseModel):
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate(cls, value: str):
        return validate_password(value)


class PasswordResetInput(NewPasswordInput):
    old_password: str


class PasswordForgotInput(BaseModel):
    email: EmailStr


class PasswordChangeOutput(BaseModel):
    message: str


class UpdateUserScore(BaseModel):
    overall_avg_score: Decimal
