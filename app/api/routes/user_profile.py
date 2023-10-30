from fastapi import APIRouter, Depends

from app.api.dependencies.repository import get_repository
from app.api.dependencies.user import get_current_user
from app.config.logs.logger import logger
from app.models.schemas.company_user import UserFullSchema
from app.repository.user import UserRepository

router = APIRouter(
    prefix="/profile",
    tags=["User profile"],
)


@router.get("/", response_model=UserFullSchema, response_model_exclude_none=True)
async def get_current_user(
    current_user: int = Depends(get_current_user),
) -> UserFullSchema:
    logger.info(f"Successfully returned current user info")
    return await UserFullSchema.from_model(current_user)
