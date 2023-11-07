from typing import Optional

from fastapi import HTTPException, status

from app.models.db.companies import RoleEnum
from app.repository.base import BaseRepository
from app.repository.company import CompanyMember, CompanyRepository
from app.utilities.validators.permission.user import validate_user_company_role


class BaseService:
    async def _validate_instance_exists(
        self, repository: BaseRepository, company_id: int
    ) -> None:
        if not await repository.exists_by_id(company_id):
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=f"{repository.model.__name__} is not found",
            )

    async def _validate_user_permissions(
        self,
        company_repository: CompanyRepository,
        company_id: int,
        current_user_id: int,
        roles: Optional[tuple[RoleEnum]] = None,
    ) -> None:
        members: list[CompanyMember] = await company_repository.get_company_members(
            company_id
        )

        if not validate_user_company_role(members, current_user_id, roles):
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Forbidden")
