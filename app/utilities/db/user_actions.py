from typing import Any, Optional

from app.repository.user import UserRepository


async def create_user_or_skip(
    user_repository: UserRepository, user_data: dict[str, bool]
) -> Optional[dict[str, Any]]:
    new_user: Optional[dict[str, Any]] = await user_repository.create_or_skip(
        user_data["email"]
    )

    # Add new user id to the user_data
    if new_user:
        user_data["id"] = new_user["id"]
        return user_data
