import re
from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, field_validator, Field
from starlette import status

from app.config.logs.logger import logger
from app.models.schemas.tags import TagSchema
from app.utilities.validators.user import validate_password


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str]

    @field_validator("name")
    def validate_user_name(cls, value):
        if not value:
            return value
        if not re.compile(r"^[a-zA-Z\- ]+$").match(value):
            logger.warning(
                f"Validation error: 'name' field contains restricted characters"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name should contain only english letters",
            )
        return value


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
    name: Optional[str] = None


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
