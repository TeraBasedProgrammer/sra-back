from typing import Optional

from pydantic import EmailStr

from app.models.db.companies import Company, RoleEnum
from app.models.db.users import User
from app.models.schemas.companies import CompanySchema, UserCompanyM2m
from app.models.schemas.users import TagBaseSchema, UserSchema


class UserFullSchema(UserSchema):
    companies: list[UserCompanyM2m]

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "string",
                "phone_number": "+380500505050",
                "id": 0,
                "registered_at": "timestamp",
                "average_score": 0,
                "tags": [{"id": 0, "title": "string"}],
                "companies": [{"id": 0, "title": "string", "role": "owner"}],
            }
        }

    @classmethod
    def from_model(cls, user_model: User):
        return cls(
            id=user_model.id,
            name=user_model.name,
            email=user_model.email,
            registered_at=user_model.registered_at,
            phone_number=user_model.phone_number,
            average_score=user_model.average_score,
            tags=[
                TagBaseSchema(id=tag.tags.id, title=tag.tags.title)
                for tag in user_model.tags
            ],
            companies=[
                UserCompanyM2m(
                    id=company.companies.id,
                    title=company.companies.title,
                    role=company.role,
                )
                for company in user_model.companies
            ],
        )


class CompanyFullSchema(CompanySchema):
    owner_email: EmailStr
    onwer_phone: Optional[str]
    onwer_name: Optional[str]
    users: list[UserCompanyM2m]

    @classmethod
    def from_model(cls, company_instance: Company):
        owner = list(
            filter(lambda u: u.role == RoleEnum.Owner, company_instance.users)
        )[0].users

        return cls(
            id=company_instance.id,
            title=company_instance.title,
            description=company_instance.description,
            created_at=company_instance.created_at,
            owner_email=owner.email,
            onwer_phone=owner.phone_number,
            onwer_name=owner.name,
            users=[
                UserCompanyM2m(
                    id=user.users.id,
                    name=user.users.name,
                    role=user.role,
                )
                for user in company_instance.users
            ],
        )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "string",
                "description": "string",
                "owner_email": "user@example.com",
                "onwer_phone": "string",
                "onwer_name": "string",
                "id": 0,
                "created_at": "2023-11-16T13:21:00.469Z",
                "users": [{"id": 0, "name": "string", "role": "owner"}],
            }
        }
