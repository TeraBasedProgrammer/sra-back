import typing

import fastapi
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.session import get_async_session
from app.repository.base import BaseRepository


def get_repository(
    repo_type: typing.Type[BaseRepository],
) -> typing.Callable[[AsyncSession], BaseRepository]:
    def _get_repo(
        async_session: AsyncSession = fastapi.Depends(get_async_session),
    ) -> BaseRepository:
        return repo_type(async_session=async_session)

    return _get_repo
