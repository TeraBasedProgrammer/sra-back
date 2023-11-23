from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import contains_eager

from app.config.logs.logger import logger
from app.models.db.companies import Company, CompanyUser, RoleEnum
from app.models.db.users import User
from app.models.schemas.companies import CompanyCreate, CompanyUpdate
from app.repository.base import BaseRepository
from app.utilities.formatters.get_args import get_args


@dataclass
class CompanyMember:
    id: int
    role: RoleEnum


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

    async def get_user_companies(self, current_user_id: int) -> list[Company]:
        query = (
            select(Company)
            .join(CompanyUser, CompanyUser.company_id == Company.id)
            .where(CompanyUser.user_id == current_user_id)
        ).with_only_columns(Company.id, Company.title, CompanyUser.role)
        response = await self.async_session.execute(query)

        result: list[Company] = response.unique()
        return result

    async def get_company_by_id(self, company_id: int, filter_string: str) -> Company:
        logger.debug(f"Received data:\n{get_args()}")

        company_user_filter = (
            (User.name.icontains(filter_string))
            | (User.phone_number.icontains(filter_string))
            | (User.email.icontains(filter_string))
        )

        query = (
            select(Company)
            .outerjoin(Company.users)
            .outerjoin(CompanyUser.users)
            .options(contains_eager(Company.users).contains_eager(CompanyUser.users))
            .where((Company.id == company_id) & company_user_filter)
        )
        result: Company = await self.get_instance(query)

        if result:
            logger.debug(f'Retrieved company by id "{company_id}": "{result}"')
        else:
            # If filtered result is None, retrieve company without users
            query = select(Company).where(Company.id == company_id)
            result: Company = await self.get_instance(query)

        return result

    async def get_company_members(self, company_id: int) -> list[CompanyMember]:
        query = (
            select(CompanyUser)
            .where(CompanyUser.company_id == company_id)
            .with_only_columns(CompanyUser.user_id, CompanyUser.role)
        )
        result: list[Company] = await self.get_many(query)
        if result:
            logger.debug(f'Retrieved company "{company_id}" members: "{result}"')

        return [CompanyMember(id=member[0], role=member[1]) for member in result]

    async def get_company_owner(self, company_id: int) -> User:
        query = (
            select(User)
            .join(CompanyUser, CompanyUser.user_id == User.id)
            .where(
                (CompanyUser.company_id == company_id)
                & (CompanyUser.role == RoleEnum.Owner)
            )
        )

        result: User = await self.get_instance(query)
        if result:
            logger.debug(f'Retrieved company "{company_id}" owner: "{result}"')

        return result

    async def update_company(
        self, company_id: int, company_data: CompanyUpdate
    ) -> Company:
        logger.debug(f"Received data:\n{get_args()}")
        updated_company = await self.update(company_id, company_data)

        logger.debug(f'Successfully updatetd company instance "{company_id}"')
        return updated_company
