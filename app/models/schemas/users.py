from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.schemas.tags import TagSchema
from app.utilities.validators.user import validate_name, validate_password


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = Field(max_length=50, min_length=2, default=None)

    @field_validator("name")
    def validate_user_name(cls, value):
        return validate_name(value)


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


class UserUpdate(BaseModel):
    name: Optional[str] = Field(max_length=50, min_length=2, default=None)

    @field_validator("name")
    def validate_user_name(cls, value):
        return validate_name(value)


class PasswordResetInput(BaseModel):
    old_password: str
    new_password: str

    @field_validator("new_password")
    def validate(cls, value: str):
        return validate_password(value)


class PasswordResetOutput(BaseModel):
    success: str = "The password was successfully reset"


class DeletedInstanceResponse(BaseModel):
    deleted_instance_id: int


class UpdateUserScore(BaseModel):
    overall_avg_score: Decimal
