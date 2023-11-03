from fastapi import APIRouter, Depends

from app.api.dependencies.services import get_company_service, get_user_service
from app.api.dependencies.user import get_current_user
from app.api.docs.user_profile import (
    get_edit_profile_responses,
    get_profile_responses,
    get_reset_password_responses,
    get_user_companies_responses,
)
from app.models.db.users import User
from app.models.schemas.companies import CompanyList
from app.models.schemas.company_user import UserFullSchema
from app.models.schemas.users import (
    PasswordChangeOutput,
    PasswordResetInput,
    UserUpdate,
)
from app.services.company import CompanyService
from app.services.user import UserService

router = APIRouter(
    prefix="/profile",
    tags=["User profile"],
)


@router.get(
    "/",
    response_model=UserFullSchema,
    responses=get_profile_responses(),
    response_model_exclude_none=True,
)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> UserFullSchema:
    """
    ### Retrieve ID and title fields of the user's companies
    """
    return await user_service.get_user_profile(current_user)


@router.get(
    "/companies",
    response_model=list[CompanyList],
    response_model_exclude_none=True,
    responses=get_user_companies_responses(),
)
async def get_user_companies(
    current_user: User = Depends(get_current_user),
    company_service: CompanyService = Depends(get_company_service),
):
    """
    ### Retrieve all user companies
    """
    return await company_service.get_user_companies(current_user)


@router.patch(
    "/edit",
    response_model=UserFullSchema,
    response_model_exclude_none=True,
    responses=get_edit_profile_responses(),
)
async def edit_user_profile(
    data: UserUpdate,
    current_user: int = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> UserFullSchema:
    """
    ### Edit user profile data
    """
    return await user_service.update_user_profile(current_user, data)


@router.patch(
    "/edit/reset_password",
    response_model=PasswordChangeOutput,
    responses=get_reset_password_responses(),
)
async def reset_password(
    data: PasswordResetInput,
    current_user: int = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> PasswordChangeOutput:
    """
    ### Reset user password
    """
    return await user_service.reset_password(current_user, data)
