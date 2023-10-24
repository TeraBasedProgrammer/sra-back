from fastapi import APIRouter, Depends

from app.api.dependencies.repository import get_repository
from app.api.dependencies.user import get_current_user_id
from app.config.logs.logger import logger
from app.models.schemas.company_user import UserFullSchema
from app.repository.user import UserRepository

router = APIRouter(
    prefix="/profile",
    tags=["User profile"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=UserFullSchema, response_model_exclude_none=True)
async def get_current_user(
    current_user_id: int = Depends(get_current_user_id),
    user_repository: UserRepository = Depends(get_repository(UserRepository)),
) -> UserFullSchema:
    logger.info(f"Accessing current user info")

    current_user = await user_repository.get_user_by_id(current_user_id)

    logger.info(f"Successfully returned current user info")
    return await UserFullSchema.from_model(current_user)
