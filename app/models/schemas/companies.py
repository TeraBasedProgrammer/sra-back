from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.db.companies import RoleEnum
from app.utilities.validators.payload.text import validate_text


class CompanyBase(BaseModel):
    title: str
    description: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_company_title(cls, value):
        return validate_text(value, "title", min_length=5, max_length=25)

    @field_validator("description")
    @classmethod
    def validate_description(cls, value):
        return validate_text(value, "description", min_length=25, max_length=3000)


class CompanyCreate(CompanyBase):
    pass


class CompanyCreateSuccess(BaseModel):
    id: int


class CompanySchema(CompanyBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class CompanyList(BaseModel):
    id: int
    title: str
    role: RoleEnum


class CompanyUsers(BaseModel):
    id: int
    name: Optional[str] = Field(None, nullable=True)
    email: Optional[str] = Field(None, nullable=True)
    phone_number: Optional[str] = Field(None, nullable=True)
    role: Optional[RoleEnum] = Field(None, nullable=True)

    class Config:
        from_attributes = True


class UserCompanies(BaseModel):
    id: int
    title: str
    role: RoleEnum


class CompanyUpdate(CompanyBase):
    title: Optional[str] = None
    description: Optional[str] = None
