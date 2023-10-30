from fastapi import APIRouter, Depends, status

from app.api.dependencies.services import get_user_service
from app.api.docs.auth import get_login_responses, get_signup_responses
from app.models.schemas.auth import (UserLoginInput, UserLoginOutput,
                                     UserSignUpInput, UserSignUpOutput)
from app.services.user import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/signup/",
    # description="Create new user account",
    response_model=UserSignUpOutput,
    status_code=201,
    responses=get_signup_responses(),
)
async def signup(
    user_data: UserSignUpInput, user_service: UserService = Depends(get_user_service)
) -> UserSignUpOutput:
    """
    ### Register a new user
    """
    return await user_service.register_user(user_data)


@router.post("/login/", response_model=UserLoginOutput, responses=get_login_responses())
async def login(
    user_data: UserLoginInput, user_service: UserService = Depends(get_user_service)
) -> UserLoginOutput:
    """
    ### Authenticate and retrieve a JWT token
    """
    return await user_service.authenticate_user(user_data)
