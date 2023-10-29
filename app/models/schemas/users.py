import re
from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, field_validator
from starlette import status

from app.config.logs.logger import logger
from app.models.schemas.tags import TagSchema


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


class UserUpdateRequest(UserBase):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    @field_validator("password")
    def validate_password(cls, value):
        if not re.compile(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$").match(value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password should contain at least eight characters, at least one letter and one number",
            )
        return value

    @field_validator("email")
    def validate_email(cls, value):
        if value is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User email can't be changed, try again",
            )
        return value


class DeletedInstanceResponse(BaseModel):
    deleted_instance_id: int


class UpdateUserScore(BaseModel):
    overall_avg_score: Decimal
