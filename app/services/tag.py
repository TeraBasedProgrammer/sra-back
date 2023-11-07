from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.models.db.companies import RoleEnum
from app.models.db.users import Tag
from app.models.schemas.tags import (
    TagBaseSchema,
    TagCreateInput,
    TagCreateOutput,
    TagSchema,
)
from app.repository.company import CompanyRepository
from app.repository.tag import TagRepository
from app.services.base import BaseService


class TagService(BaseService):
    def __init__(self, tag_repository, company_repository) -> None:
        self.tag_repository: TagRepository = tag_repository
        self.company_repository: CompanyRepository = company_repository

    async def create_tag(
        self, tag_data: TagCreateInput, current_user_id: int
    ) -> TagCreateInput:
        await self._validate_instance_exists(
            self.company_repository, tag_data.company_id
        )
        await self._validate_user_permissions(
            self.company_repository,
            tag_data.company_id,
            current_user_id,
            (RoleEnum.Owner, RoleEnum.Admin),
        )

        try:
            new_tag_id = await self.tag_repository.create_tag(tag_data)
            return TagCreateOutput(tag_id=new_tag_id)
        except IntegrityError:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail="The company already has a tag with provided title, try again",
            )

    async def get_company_tags(
        self, current_user_id: int, company_id: int
    ) -> list[TagBaseSchema]:
        await self._validate_instance_exists(company_id)
        await self._validate_user_permissions(company_id, current_user_id)

        tags: list[Tag] = await self.tag_repository.get_company_tags(company_id)
        return [TagBaseSchema(id=tag.id, title=tag.title) for tag in tags]

    async def get_tag_by_id(self, current_user_id: int, tag_id: int) -> TagSchema:
        if not await self.tag_repository.exists_by_id(tag_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Tag is not found")

        tag = await self.tag_repository.get_tag_by_id(tag_id)

        await self._validate_instance_exists(tag.company_id)
        await self._validate_user_permissions(tag.company_id, current_user_id)

        return TagSchema(
            id=tag.id,
            title=tag.title,
            description=tag.description,
        )
