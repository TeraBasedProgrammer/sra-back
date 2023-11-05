from sqlalchemy import select

from app.config.logs.logger import logger
from app.models.db.users import Tag
from app.repository.base import BaseRepository
from app.utilities.formatters.get_args import get_args


class TagRepository(BaseRepository):
    model = Tag

    async def exists_by_id(self, tag_id: int) -> bool:
        logger.debug(f"Received data:\n{get_args()}")

        query = select(Tag).where(Tag.id == tag_id)
        return await self.exists(query)

    async def get_company_tags(self, company_id) -> list[Tag]:
        result = await self.async_session.execute(
            select(Tag)
            .where(Tag.company_id == company_id)
            .with_only_columns(Tag.id, Tag.title)
        )
        return result.scalars().all()

    async def get_tag_by_id(self, tag_id) -> Tag:
        logger.debug(f"Received data:\n{get_args()}")

        query = select(Tag).where(Tag.id == tag_id)
        result: Tag = await self.get_instance(query)
        if result:
            logger.debug(f'Retrieved tag by id "{tag_id}": "{result}"')
        return result
