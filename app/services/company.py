from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.models.db.users import User
from app.models.schemas.companies import CompanyCreate, CompanyCreateSuccess
from app.repository.company import CompanyRepository
from app.utilities.formatters.http_error import validation_error_wrapper


class CompanyService:
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

    async def get_user_companies(self):
        return await self.company_repository.get_user_companies()

    async def get_company_by_id(self):
        pass
