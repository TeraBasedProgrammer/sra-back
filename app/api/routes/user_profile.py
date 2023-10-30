from fastapi import APIRouter, Depends

from app.api.dependencies.user import get_current_user
from app.models.schemas.company_user import UserFullSchema
from app.services.user import UserService
from app.api.dependencies.services import get_user_service

router = APIRouter(
    prefix="/profile",
    tags=["User profile"],
)


@router.get("/", response_model=UserFullSchema, response_model_exclude_none=True)
async def get_current_user(
    current_user: int = Depends(get_current_user), user_service: UserService = Depends(get_user_service)
) -> UserFullSchema:
    return await user_service.get_user_profile(current_user)
