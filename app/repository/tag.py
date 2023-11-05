from sqlalchemy import select

from app.models.db.users import Tag
from app.repository.base import BaseRepository


class TagRepository(BaseRepository):
    model = Tag

    async def get_company_tags(self, company_id) -> list[Tag]:
        result = await self.async_session.execute(
            select(Tag).where(Tag.company_id == company_id)
        )
        return result.scalars().all()
