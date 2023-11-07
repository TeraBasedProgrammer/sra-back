from fastapi import APIRouter, Depends

from app.api.dependencies.services import get_user_service
from app.api.docs.auth import auth_docs
from app.models.schemas.auth import (
    UserLoginInput,
    UserLoginOutput,
    UserSignUpInput,
    UserSignUpOutput,
)
from app.models.schemas.users import (
    NewPasswordInput,
    PasswordChangeOutput,
    PasswordForgotInput,
)
from app.services.user import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/signup/",
    response_model=UserSignUpOutput,
    status_code=201,
    responses=auth_docs.signup(),
)
async def signup(
    user_data: UserSignUpInput, user_service: UserService = Depends(get_user_service)
) -> UserSignUpOutput:
    """
    ### Register a new user
    """
    return await user_service.register_user(user_data)


@router.post("/login/", response_model=UserLoginOutput, responses=auth_docs.login())
async def login(
    user_data: UserLoginInput, user_service: UserService = Depends(get_user_service)
) -> UserLoginOutput:
    """
    ### Authenticate and retrieve a JWT token
    """
    return await user_service.authenticate_user(user_data)


@router.post(
    "/forgot-password/",
    response_model=PasswordChangeOutput,
    responses=auth_docs.forgot_password(),
)
async def forgot_password(
    data: PasswordForgotInput, user_service: UserService = Depends(get_user_service)
) -> PasswordChangeOutput:
    """
    ### Pass the existing email to recieve password restoration link on the email

    ### Steps to perform password change on the frontend side:

    1. When user clicks on the reset link, you should perform secret HTTP request to the `/auth/forgot-password/verify-code/` endpoint.
        - If the response code is 200, render the form page
        - If the response code is either 400 or 422, render the error page
    2. Save the reset code (query parameter) and send it to the `/auth/forgot-password/reset/` endpoint alongside the payload
    """
    return await user_service.handle_forgot_password(data.email)


@router.post(
    "/forgot-password/verify-code/",
    response_model=dict[str, str],
    responses=auth_docs.verify_reset_password_code(),
)
async def verify_reset_password_code(
    code: str, user_service: UserService = Depends(get_user_service)
) -> dict[str, str]:
    """
    ### Pass the reset code and get a response
    """
    return await user_service.verify_code(code)


@router.post(
    "/forgot-password/reset/",
    response_model=dict[str, str],
    responses=auth_docs.reset_forgotten_password(),
)
async def reset_password(
    code: str,
    data: NewPasswordInput,
    user_service: UserService = Depends(get_user_service),
) -> dict[str, str]:
    """
    ### Pass the reset code and get a response
    """
    return await user_service.reset_forgotten_password(data.new_password, code)
