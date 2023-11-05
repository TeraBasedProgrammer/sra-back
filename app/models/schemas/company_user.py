from app.models.db.companies import Company
from app.models.db.users import User
from app.models.schemas.companies import CompanySchema, UserCompanyM2m
from app.models.schemas.users import TagBaseSchema, UserSchema


class UserFullSchema(UserSchema):
    companies: list[UserCompanyM2m]

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
    users: list[UserCompanyM2m]

    @classmethod
    def from_model(cls, company_model: Company):
        return cls(
            id=company_model.id,
            title=company_model.title,
            description=company_model.description,
            created_at=company_model.created_at,
            users=[
                UserCompanyM2m(
                    id=user.users.id,
                    name=user.users.name,
                    role=user.role,
                )
                for user in company_model.users
            ],
        )
