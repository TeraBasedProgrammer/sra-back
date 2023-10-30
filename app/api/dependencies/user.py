from typing import Any

from fastapi import Depends

from app.api.dependencies.auth import auth_wrapper
from app.api.dependencies.repository import get_repository
from app.models.db.users import User
from app.repository.user import UserRepository


async def get_current_user(
    auth_data: dict[str, Any] = Depends(auth_wrapper),
    user_repository: UserRepository = Depends(get_repository(UserRepository)),
) -> int:
    current_user: User = await user_repository.get_user_by_email(auth_data["email"])
    return current_user
