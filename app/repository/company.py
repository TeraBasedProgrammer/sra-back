from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.config.logs.logger import logger
from app.models.db.companies import Company, CompanyUser
from app.models.db.users import User
from app.models.schemas.companies import CompanyCreate, CompanyList
from app.repository.base import BaseRepository
from app.utilities.formatters.get_args import get_args


class CompanyRepository(BaseRepository):
    model = Company

    async def create_company(
        self, company_data: CompanyCreate, current_user: User
    ) -> int:
        logger.debug(f"Received data:\n{get_args()}")

        new_company: Company = await self.create(company_data)

        # Create m2m model between User and Company
        company_user_object = CompanyUser(
            company_id=new_company.id, user_id=current_user.id
        )
        await self.save(company_user_object)

        logger.debug("Successfully inserted new company instance into the database")
        return new_company.id

    async def exists_by_id(self, company_id: int):
        logger.debug(f"Received data:\n{get_args()}")

        query = select(Company).where(Company.id == company_id)
        return await self.exists(query)

    async def get_user_companies(self, current_user: User) -> list[CompanyList]:
        query = (
            select(Company)
            .options(joinedload(Company.users))
            .where(CompanyUser.user_id == current_user.id)
        ).with_only_columns(Company.id, Company.title)
        response = await self.async_session.execute(query)
        result: list[Company] = response.unique()
        if result:
            return [
                CompanyList(id=company.id, title=company.title) for company in result
            ]
        return []

    async def get_company_by_id(self, company_id: int) -> Company:
        logger.debug(f"Received data:\n{get_args()}")

        query = (
            select(Company)
            .options(joinedload(Company.users))
            .where(Company.id == company_id)
        )
        result: Optional[Company] = await self.get_instance(query)
        if result:
            logger.debug(f'Retrieved company by id "{company_id}": "{result}"')
        return result
