from app.config.logs.logger import logger
from app.models.db.companies import Company, CompanyUser
from app.models.db.users import User
from app.models.schemas.companies import CompanyCreate
from app.repository.base import BaseRepository
from app.utilities.formatters.get_args import get_args


class CompanyRepository(BaseRepository):
    model = Company

    async def create_company(
        self, company_data: CompanyCreate, current_user: User
    ) -> int:
        logger.debug(f"Received data:\n{get_args(1)}")

        new_company: Company = await self.create(company_data)

        # Create m2m model between User and Company
        company_user_object = CompanyUser(
            company_id=new_company.id, user_id=current_user.id
        )
        await self.save(company_user_object)

        logger.debug("Successfully inserted new company instance into the database")
        return new_company.id

    async def get_user_companies(self) -> list[Company]:
        raise NotImplementedError()

    async def get_company_by_id(self) -> Company:
        raise NotImplementedError()
