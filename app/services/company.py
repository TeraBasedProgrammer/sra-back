from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.models.db.users import User
from app.models.schemas.companies import CompanyCreate, CompanyCreateSuccess
from app.models.schemas.company_user import CompanyFullSchema
from app.repository.company import CompanyRepository
from app.services.base import BaseService
from app.utilities.formatters.http_error import validation_error_wrapper


class CompanyService(BaseService):
    def __init__(self, company_repository) -> None:
        self.company_repository: CompanyRepository = company_repository

    async def create_company(
        self, company_data: CompanyCreate, current_user: User
    ) -> CompanyCreateSuccess:
        try:
            company_id = await self.company_repository.create_company(
                company_data, current_user
            )

            return CompanyCreateSuccess(id=company_id)
        except IntegrityError:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=validation_error_wrapper(
                    "Company with this title already exists", "title"
                ),
            )

    async def get_user_companies(self, current_user: User):
        return await self.company_repository.get_user_companies(current_user)

    async def get_company_by_id(self, company_id: int) -> CompanyFullSchema:
        await self._validate_instance_exists(self.company_repository, company_id)

        company = await self.company_repository.get_company_by_id(company_id)
        return CompanyFullSchema.from_model(company)
