from typing import Any

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
)
from app.models.schemas.company_user import CompanyFullSchema
from app.models.schemas.users import CompanyMemberInput, UserCreate
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

    async def get_user_companies(self, current_user: User):
        return await self.company_repository.get_user_companies(current_user)

    async def get_company_by_id(self, company_id: int) -> CompanyFullSchema:
        await self._validate_instance_exists(self.company_repository, company_id)

        company = await self.company_repository.get_company_by_id(company_id)
        return CompanyFullSchema.from_model(company)

    async def update_company(
        self, company_id: int, company_data: CompanyUpdate, current_user_id: int
    ) -> CompanyFullSchema:
        await self._validate_instance_exists(self.company_repository, company_id)

        new_fields: dict = company_data.model_dump(exclude_none=True)
        if new_fields == {}:
            logger.warning("Validation error: No parameters have been provided")
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=error_wrapper(
                    "At least one valid field should be provided", None
                ),
            )

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

        # Validate passed role
        if member_data.role not in ["admin", "tester", "employee"]:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=error_wrapper("Invalid role", "role"),
            )

        # Validate passed tag ids
        if not await self.tag_repository.tags_exist_by_id(member_data.tags):
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=error_wrapper(
                    "One or more tags are not found. Ensure you passed the correct values",
                    "tags",
                ),
            )

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
