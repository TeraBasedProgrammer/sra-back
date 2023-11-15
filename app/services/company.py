from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.config.logs.logger import logger
from app.models.db.companies import Company, CompanyUser, RoleEnum
from app.models.db.users import TagUser, User
from app.models.schemas.auth import UserSignUpOutput
from app.models.schemas.companies import (
    CompanyCreate,
    CompanyCreateSuccess,
    CompanyUpdate,
    UserCompanyM2m,
)
from app.models.schemas.company_user import CompanyFullSchema, UserFullSchema
from app.models.schemas.users import CompanyMemberInput, CompanyMemberUpdate, UserCreate
from app.repository.company import CompanyRepository
from app.repository.tag import TagRepository
from app.repository.user import UserRepository
from app.securities.authorization.auth_handler import auth_handler
from app.services.base import BaseService
from app.utilities.formatters.http_error import error_wrapper


class CompanyService(BaseService):
    def __init__(self, company_repository, user_repository, tag_repository) -> None:
        self.company_repository: CompanyRepository = company_repository
        self.user_repository: UserRepository = user_repository
        self.tag_repository: TagRepository = tag_repository

    async def _validate_passed_role(self, member_data: Any) -> None:
        if member_data.role not in ["admin", "tester", "employee"]:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=error_wrapper("Invalid role", "role"),
            )

    async def _validate_tag_ids(self, member_data: Any) -> None:
        if not await self.tag_repository.tags_exist_by_id(member_data.tags):
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=error_wrapper(
                    "One or more tags are not found. Ensure you passed the correct values",
                    "tags",
                ),
            )

    def _validate_not_same_id(
        self, current_user_id: int, member_id: int, error_message: str
    ) -> None:
        if current_user_id == member_id:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=error_wrapper(error_message, "member_id"),
            )

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
                detail=error_wrapper("Company with this title already exists", "title"),
            )

    async def get_user_companies(
        self, current_user_id: int
    ) -> Optional[list[UserCompanyM2m]]:
        companies: list[Company] = await self.company_repository.get_user_companies(
            current_user_id
        )
        if companies:
            return [
                UserCompanyM2m(title=company.title, role=company.role, id=company.id)
                for company in companies
            ]

        return []

    async def get_company_by_id(self, company_id: int) -> CompanyFullSchema:
        await self._validate_instance_exists(self.company_repository, company_id)

        company = await self.company_repository.get_company_by_id(company_id)
        return CompanyFullSchema.from_model(company)

    async def update_company(
        self, company_id: int, company_data: CompanyUpdate, current_user_id: int
    ) -> CompanyFullSchema:
        await self._validate_instance_exists(self.company_repository, company_id)
        self._validate_update_data(company_data)
        await self._validate_user_permissions(
            self.company_repository,
            company_id,
            current_user_id,
            (RoleEnum.Owner,),
        )

        await self.company_repository.update_company(company_id, company_data)
        updated_company: Company = await self.company_repository.get_company_by_id(
            company_id
        )
        return CompanyFullSchema.from_model(updated_company)

    async def get_member(
        self, company_id: int, member_id: int, current_user_id: int
    ) -> UserFullSchema:
        await self._validate_instance_exists(self.company_repository, company_id)
        await self._validate_user_permissions(
            self.company_repository,
            company_id,
            current_user_id,
        )

        # Validate if user with 'member_id' exists and is a company member
        await self._validate_company_member(
            self.user_repository, self.company_repository, member_id, company_id
        )

        user = await self.user_repository.get_user_by_id(member_id)
        return UserFullSchema.from_model(user)

    async def add_member(
        self, company_id: int, member_data: CompanyMemberInput, current_user_id: int
    ) -> UserSignUpOutput:
        await self._validate_instance_exists(self.company_repository, company_id)
        await self._validate_user_permissions(
            self.company_repository,
            company_id,
            current_user_id,
            (RoleEnum.Owner, RoleEnum.Admin),
        )

        await self._validate_passed_role(member_data)
        await self._validate_tag_ids(member_data)

        # Hash user password
        member_data.password = auth_handler.get_password_hash(member_data.password)

        try:
            # Create new company member database instances
            new_user: dict[str, Any] = await self.user_repository.create_user(
                UserCreate(
                    email=member_data.email,
                    name=member_data.name,
                    phone_number=member_data.phone_number,
                    password=member_data.password,
                )
            )
            new_company_user = CompanyUser(
                company_id=company_id,
                user_id=new_user.get("id"),
                role=RoleEnum(member_data.role),
            )
            new_tag_users: list[TagUser] = [
                TagUser(tag_id=tag_id, user_id=new_user.get("id"))
                for tag_id in member_data.tags
            ]

            # Save new M2M objects explicitly
            await self.company_repository.save(new_company_user)
            for tag_user in new_tag_users:
                await self.tag_repository.save(tag_user)

            return new_user
        except IntegrityError:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail=error_wrapper("User with this email already exists", "email"),
            )

    async def update_member(
        self,
        company_id: int,
        member_id: int,
        member_data: CompanyMemberUpdate,
        current_user_id: int,
    ) -> UserFullSchema:
        await self._validate_instance_exists(self.company_repository, company_id)
        await self._validate_user_permissions(
            self.company_repository,
            company_id,
            current_user_id,
            (RoleEnum.Owner, RoleEnum.Admin),
        )
        self._validate_update_data(member_data)

        # Validate if user with 'member_id' exists and is a company member
        await self._validate_company_member(
            self.user_repository, self.company_repository, member_id, company_id
        )

        # Validate if user tries to update its data
        self._validate_not_same_id(
            current_user_id, member_id, "You can't change your own company data"
        )

        # Validate if member user is not the owner
        member = await self.user_repository.get_user_by_id(member_id)
        for company in member.companies:
            if company.companies.id == company_id and company.role == RoleEnum.Owner:
                raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Forbidden")

        if member_data.tags:
            await self._validate_tag_ids(member_data)

            # Recreate tags for the member
            await self.user_repository.delete_related_tag_user(member_id)
            logger.critical(type(member.tags))
            await self.user_repository.save_many(
                [TagUser(user_id=member_id, tag_id=tag) for tag in member_data.tags]
            )

        if member_data.role:
            await self._validate_passed_role(member_data)
            member.companies[0].role = RoleEnum(member_data.role)
            await self.user_repository.save(member)

        new_member = await self.user_repository.get_user_by_id(member_id)
        return UserFullSchema.from_model(new_member)

    async def delete_member(self, company_id, member_id, current_user_id) -> None:
        await self._validate_instance_exists(self.company_repository, company_id)
        await self._validate_user_permissions(
            self.company_repository,
            company_id,
            current_user_id,
            (RoleEnum.Owner, RoleEnum.Admin),
        )

        # Validate if user with 'member_id' exists and is a company member
        await self._validate_company_member(
            self.user_repository, self.company_repository, member_id, company_id
        )

        # Validate if user tries to update its data
        self._validate_not_same_id(
            current_user_id, member_id, "You can't delete yourself from the company"
        )

        # Validate if member user is not the owner
        company_members = await self.company_repository.get_company_members(company_id)
        for member in company_members:
            if member.id == member_id and member.role == RoleEnum.Owner:
                raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Forbidden")

        await self.user_repository.delete_user(member_id)
