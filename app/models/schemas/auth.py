import re
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, field_validator
from starlette import status

from app.config.logs.logger import logger
from app.models.schemas.users import UserBase


class UserSignUpInput(UserBase):
    password: str
    name: Optional[str] = None

    @field_validator("password")
    def validate_password(cls, value):
        if not re.compile(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$").match(value):
            logger.warning(f"Validation error: password doesn't match the pattern")
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="Password should contain at least eight characters, at least one letter and one number",
            )
        return value


class UserSignUpAuth0(UserSignUpInput):
    auth0_registered: bool


class UserSignUpOutput(BaseModel):
    id: int
    email: EmailStr


class UserLoginInput(BaseModel):
    email: EmailStr
    password: str


class UserLoginOutput(BaseModel):
    token: str
