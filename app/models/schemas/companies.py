from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.db.companies import RoleEnum
from app.utilities.validators.text import validate_text


class CompanyBase(BaseModel):
    title: str = Field(max_length=25, min_length=5)
    description: str

    @field_validator("title")
    @classmethod
    def validate_company_title(cls, value):
        return validate_text(value, "title")

    @field_validator("description")
    @classmethod
    def validate_description(cls, value):
        return validate_text(value, "description")


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


class UserCompanyM2m(BaseModel):
    id: int
    title: Optional[str] = Field(None, nullable=True)
    name: Optional[str] = Field(None, nullable=True)
    role: Optional[RoleEnum] = Field(None, nullable=True)

    class Config:
        from_attributes = True


class CompanyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
