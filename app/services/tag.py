from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.config.logs.logger import logger
from app.models.db.companies import RoleEnum
from app.models.db.users import Tag
from app.models.schemas.tags import (
    TagBaseSchema,
    TagCreateInput,
    TagCreateOutput,
    TagSchema,
    TagUpdateInput,
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
        await self._validate_instance_exists(self.company_repository, company_id)
        await self._validate_user_permissions(
            self.company_repository, company_id, current_user_id
        )

        tags: list[Tag] = await self.tag_repository.get_company_tags(company_id)
        return [TagBaseSchema(id=tag.id, title=tag.title) for tag in tags]

    async def get_tag_by_id(self, current_user_id: int, tag_id: int) -> TagSchema:
        if not await self.tag_repository.exists_by_id(tag_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Tag is not found")

        tag = await self.tag_repository.get_tag_by_id(tag_id)

        await self._validate_instance_exists(self.company_repository, tag.company_id)
        await self._validate_user_permissions(
            self.company_repository, tag.company_id, current_user_id
        )

        return TagSchema(
            id=tag.id,
            title=tag.title,
            description=tag.description,
        )

    async def update_tag(
        self, tag_id: int, tag_data: TagUpdateInput, current_user_id: int
    ) -> TagSchema:
        await self._validate_instance_exists(self.tag_repository, tag_id)

        new_fields: dict = tag_data.model_dump(exclude_none=True)
        if new_fields == {}:
            logger.warning("Validation error: No parameters have been provided")
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="At least one valid field should be provided",
            )

        tag = await self.tag_repository.get_tag_by_id(tag_id)

        await self._validate_user_permissions(
            self.company_repository,
            tag.company_id,
            current_user_id,
            (RoleEnum.Owner, RoleEnum.Admin),
        )

        updated_tag: Tag = await self.tag_repository.update_tag(tag_id, tag_data)
        return TagSchema(
            id=updated_tag.id,
            title=updated_tag.title,
            description=updated_tag.description,
        )

    async def delete_tag(self, tag_id: int, current_user_id: int) -> None:
        await self._validate_instance_exists(self.tag_repository, tag_id)

        tag = await self.tag_repository.get_tag_by_id(tag_id)

        await self._validate_user_permissions(
            self.company_repository,
            tag.company_id,
            current_user_id,
            (RoleEnum.Owner, RoleEnum.Admin),
        )

        await self.tag_repository.delete_tag(tag_id)
