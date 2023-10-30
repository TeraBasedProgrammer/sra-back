from fastapi import Depends

from app.api.dependencies.repository import get_repository
from app.repository.user import UserRepository
from app.services.user import UserService


def get_user_service(
    user_repository: UserRepository = Depends(get_repository(UserRepository)),
) -> UserService:
    service = UserService(user_repository)
    return service
