from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    def __init__(self, async_session: AsyncSession):
        self.async_session = async_session
