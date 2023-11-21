from fastapi import APIRouter, Depends

from app.api.dependencies.services import get_company_service, get_user_service
from app.api.dependencies.user import get_current_user, get_current_user_id
from app.api.docs.user_profile import user_profile_docs
from app.models.db.users import User
from app.models.schemas.companies import UserCompanyM2m
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
    responses=user_profile_docs.get_user_profile(),
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
    "/companies/",
    response_model=list[UserCompanyM2m],
    response_model_exclude_none=True,
    responses=user_profile_docs.get_user_companies(),
)
async def get_user_companies(
    current_user_id: int = Depends(get_current_user_id),
    company_service: CompanyService = Depends(get_company_service),
) -> list[UserCompanyM2m]:
    """
    ### Retrieve all user companies
    """
    return await company_service.get_user_companies(current_user_id)


@router.patch(
    "/edit/",
    response_model=UserFullSchema,
    response_model_exclude_none=True,
    responses=user_profile_docs.edit_user_profile(),
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
    "/edit/reset_password/",
    response_model=PasswordChangeOutput,
    responses=user_profile_docs.reset_password(),
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
