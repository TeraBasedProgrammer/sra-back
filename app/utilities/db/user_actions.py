from typing import Any, Optional

from app.api.dependencies.repository import get_repository
from app.repository.user import UserRepository


async def create_user_or_skip(user_data: dict[str, bool]):
    user_crud: UserRepository = get_repository(UserRepository)
    new_user: Optional[dict[str, Any]] = await user_crud.error_or_create(
        user_data["email"]
    )

    # Add new user id to the user_data
    if new_user:
        user_data["id"] = new_user["id"]
        return user_data