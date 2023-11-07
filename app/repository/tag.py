from sqlalchemy import select
from sqlalchemy.orm import load_only

from app.config.logs.logger import logger
from app.models.db.users import Tag
from app.models.schemas.tags import TagCreateInput
from app.repository.base import BaseRepository
from app.utilities.formatters.get_args import get_args


class TagRepository(BaseRepository):
    model = Tag

    async def create_tag(self, tag_data: TagCreateInput) -> int:
        logger.debug(f"Received data:\n{get_args()}")

        new_tag: Tag = await self.create(tag_data)

        logger.debug("Successfully inserted new tag instance into the database")
        return new_tag.id

    async def get_company_tags(self, company_id) -> list[Tag]:
        result = await self.async_session.execute(
            select(Tag)
            .options(load_only(Tag.id, Tag.title))
            .where(Tag.company_id == company_id)
        )
        return result.scalars().all()

    async def get_tag_by_id(self, tag_id) -> Tag:
        logger.debug(f"Received data:\n{get_args()}")

        query = select(Tag).where(Tag.id == tag_id)
        result: Tag = await self.get_instance(query)
        if result:
            logger.debug(f'Retrieved tag by id "{tag_id}": "{result}"')
        return result
