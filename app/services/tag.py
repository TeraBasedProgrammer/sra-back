from fastapi import HTTPException, status

from app.models.db.users import Tag
from app.models.schemas.tags import TagBaseSchema, TagSchema
from app.repository.company import CompanyMember, CompanyRepository
from app.repository.tag import TagRepository
from app.utilities.validators.permission.user import validate_user_company_role


class TagService:
    def __init__(self, tag_repository, company_repository) -> None:
        self.tag_repository: TagRepository = tag_repository
        self.company_repository: CompanyRepository = company_repository

    async def get_company_tags(
        self, current_user_id: int, company_id: int
    ) -> list[TagBaseSchema]:
        if not await self.company_repository.exists_by_id(company_id):
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail="Company is not found"
            )

        members: list[
            CompanyMember
        ] = await self.company_repository.get_company_members(company_id)
        if not validate_user_company_role(members, current_user_id):
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Forbidden")

        tags: list[Tag] = await self.tag_repository.get_company_tags(company_id)
        return [TagBaseSchema(id=tag.id, title=tag.title) for tag in tags]

    async def get_tag_by_id(self, tag_id: int) -> TagSchema:
        if not self.tag_repository.exists_by_id(tag_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Tag is not found")

        # tag = self.tag_repository.get_tag_by_id(tag_id)
