from fastapi import APIRouter, Depends

from app.api.dependencies.services import get_user_service
from app.api.dependencies.user import get_current_user
from app.api.docs.user_profile import (get_profile_responses,
                                       get_reset_password_responses)
from app.models.schemas.company_user import UserFullSchema
from app.models.schemas.users import PasswordResetInput, PasswordResetOutput
from app.services.user import UserService

router = APIRouter(
    prefix="/profile",
    tags=["User profile"],
)


@router.get(
    "/",
    response_model=UserFullSchema,
    response_model_exclude_none=True,
    responses=get_profile_responses(),
)
async def get_user_profile(
    current_user: int = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> UserFullSchema:
    return await user_service.get_user_profile(current_user)


@router.patch("/edit", response_model=None)
async def edit_user_profile(
    data: None,
    current_user: int = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> None:
    return await user_service.update_user_profile(current_user)


@router.patch(
    "/edit/reset_password",
    response_model=PasswordResetOutput,
    responses=get_reset_password_responses(),
)
async def reset_password(
    data: PasswordResetInput,
    current_user: int = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> PasswordResetOutput:
    return await user_service.reset_password(current_user, data)
