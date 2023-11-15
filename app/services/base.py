from typing import Optional

from fastapi import HTTPException, status
from pydantic import BaseModel

from app.config.logs.logger import logger
from app.models.db.companies import RoleEnum
from app.repository.base import BaseRepository
from app.repository.company import CompanyMember, CompanyRepository
from app.repository.user import UserRepository
from app.utilities.formatters.http_error import error_wrapper
from app.utilities.validators.permission.user import validate_user_company_role


class BaseService:
    async def _validate_instance_exists(
        self, repository: BaseRepository, instance_id: int
    ) -> None:
        if not await repository.exists_by_id(instance_id):
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=f"{repository.model.__name__} is not found",
            )

    async def _validate_user_permissions(
        self,
        company_repository: CompanyRepository,
        company_id: int,
        user_id: int,
        roles: Optional[tuple[RoleEnum]] = None,
        raise_exception: bool = True,
    ) -> None:
        members: list[CompanyMember] = await company_repository.get_company_members(
            company_id
        )
        is_member = validate_user_company_role(members, user_id, roles)
        if not is_member and raise_exception:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Forbidden")

        return is_member

    def _validate_update_data(self, update_data: BaseModel) -> None:
        new_fields: dict = update_data.model_dump(exclude_none=True)
        if new_fields == {}:
            logger.warning("Validation error: No parameters have been provided")
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=error_wrapper(
                    "At least one valid field should be provided", None
                ),
            )

    async def _validate_company_member(
        self,
        user_repository: UserRepository,
        company_repository: CompanyRepository,
        member_id: int,
        company_id: int,
    ) -> None:
        member_user_exists = user_repository.exists_by_id(member_id)
        if not member_user_exists:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Member is not found")

        user_is_member = await self._validate_user_permissions(
            company_repository, company_id, member_id, raise_exception=False
        )

        if not user_is_member:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Member is not found")
