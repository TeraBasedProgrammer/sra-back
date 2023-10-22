from typing import AsyncGenerator

import redis.asyncio as rd
from sqlalchemy.ext.asyncio import (AsyncAttrs, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.orm import DeclarativeBase

from app.config.settings.base import settings
from app.config.logs.logger import logger


DATABASE_URL: str = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

logger.critical(settings.REDIS_URL)
redis = rd.from_url("redis://redis.sra:6379", decode_responses=True, encoding="utf-8", db=0)


class Base(AsyncAttrs, DeclarativeBase):
    pass


engine = create_async_engine(
    DATABASE_URL,
    echo=True
)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
