from typing import Any

from fastapi import Depends

from app.api.dependencies.auth import auth_wrapper
from app.api.dependencies.repository import get_repository
from app.models.db.users import User
from app.repository.user import UserRepository


async def get_current_user(
    auth_data: dict[str, Any] = Depends(auth_wrapper),
    user_repository: UserRepository = Depends(get_repository(UserRepository)),
) -> User:
    current_user: User = await user_repository.get_user_by_email(auth_data["email"])
    return current_user


async def get_current_user_id(
    auth_data: dict[str, Any] = Depends(auth_wrapper),
    user_repository: UserRepository = Depends(get_repository(UserRepository)),
) -> int:
    user_id: int = (
        await user_repository.get_user_id(auth_data.get("email"))
        if not auth_data.get("id")
        else auth_data.get("id")
    )

    return user_id
