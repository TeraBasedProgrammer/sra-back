from typing import Optional

from pydantic import EmailStr
from sqlalchemy.exc import MissingGreenlet

from app.models.db.companies import Company
from app.models.db.users import User
from app.models.schemas.companies import CompanySchema, CompanyUsers, UserCompanies
from app.models.schemas.users import TagBaseSchema, UserSchema


class UserFullSchema(UserSchema):
    companies: list[UserCompanies]

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
                UserCompanies(
                    id=company.companies.id,
                    title=company.companies.title,
                    role=company.role,
                )
                for company in user_model.companies
            ],
        )


class CompanyFullSchema(CompanySchema):
    staff_count: int
    owner_email: EmailStr
    owner_phone: Optional[str]
    owner_name: Optional[str]
    users: list[CompanyUsers]

    @classmethod
    def _initialize_schema_instance(
        cls,
        company_instance: Company,
        staff_count: int,
        owner_instance: User,
        users: Optional[list[User]],
    ):
        return cls(
            id=company_instance.id,
            title=company_instance.title,
            description=company_instance.description,
            staff_count=staff_count,
            created_at=company_instance.created_at,
            owner_email=owner_instance.email,
            owner_phone=owner_instance.phone_number,
            owner_name=owner_instance.name,
            users=[
                CompanyUsers(
                    id=user.users.id,
                    name=user.users.name,
                    phone_number=user.users.phone_number,
                    email=user.users.email,
                    role=user.role,
                )
                for user in users
            ],
        )

    @classmethod
    def from_model(
        cls, company_instance: Company, staff_count: int, owner_instance: User
    ):
        # Validate if Company's users field is empty
        try:
            return cls._initialize_schema_instance(
                company_instance, staff_count, owner_instance, company_instance.users
            )
        except MissingGreenlet:
            return cls._initialize_schema_instance(
                company_instance, staff_count, owner_instance, []
            )
