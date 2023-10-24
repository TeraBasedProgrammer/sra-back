from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.utilities.validators.text import validate_text
from app.models.db.companies import RoleEnum



class CompanyBase(BaseModel):
    title: str = Field(max_length=100)
    description: str

    @field_validator("title")
    def validate_company_title(cls, value):
        return validate_text(value)
    
    
class CompanySchema(CompanyBase):
    id: int 
    created_at: datetime
    role: Optional[RoleEnum] = Field(None, nullable=True)
    
    class Config:
        from_attributes = True
        populate_by_name = True


class UserCompanySchema(BaseModel):
    id: int
    title: str
    role: Optional[RoleEnum] = Field(None, nullable=True)
    
    class Config:
        from_attributes = True
        populate_by_name = True
        

class CompanyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_hidden: Optional[bool] = None
    