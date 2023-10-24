from typing import Optional

from app.models.schemas.companies import UserCompanySchema
from app.models.schemas.users import UserSchema
from app.models.db.users import User


class UserFullSchema(UserSchema):
    companies: Optional[list[UserCompanySchema]] = []
     
    @classmethod
    async def from_model(cls, user_model: User):
        return cls(
            id=user_model.id,
            name=user_model.name,
            email=user_model.email,
            registered_at=user_model.registered_at,
            average_score=user_model.average_score,
            tags=user_model.tags,
            companies=[
                UserCompanySchema(
                    id=company.companies.id,
                    title=company.companies.title,
                    role=company.role,
                )
                for company in user_model.companies 
            ]
        )
