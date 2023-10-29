from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.repository import get_repository
from app.config.logs.logger import logger
from app.models.schemas.auth import (UserLoginInput, UserLoginOutput,
                                     UserSignUpInput, UserSignUpOutput)
from app.repository.user import UserRepository
from app.securities.authorization.auth_handler import auth_handler


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup/", response_model=UserSignUpOutput, status_code=201)
async def signup(
    user: UserSignUpInput,
    user_crud: UserRepository = Depends(get_repository(UserRepository)),
) -> UserSignUpOutput:
    logger.info(f"Creating new User instance")

    user_existing_object = await user_crud.get_user_by_email(user.email)
    if user_existing_object:
        logger.warning(
            f'Validation error: User with email "{user.email}" already exists'
        )
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )
    result = await user_crud.create_user(user)
    logger.info(f"New user instance has been successfully created")
    return result


@router.post(
    "/login/", response_model=UserLoginOutput,
)
async def login(
    user_data: UserLoginInput,
    user_crud: UserRepository = Depends(get_repository(UserRepository)),
) -> Optional[dict[str, str]]:
    logger.info(f'Login attempt with email "{user_data.email}"')

    user_existing_object = await user_crud.get_user_by_email(user_data.email)
    if not user_existing_object:
        logger.warning(
            f'User with email "{user_data.email}" is not registered in the system'
        )
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="User with this email is not registered in the system"
        )

    verify_password = await auth_handler.verify_password(
        user_data.password, user_existing_object.password
    )
    if not verify_password:
        logger.warning(f"Invalid password was provided")
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Invalid password"
        )
    logger.info(f'User "{user_data.email}" successfully logged in the system')
    auth_token = await auth_handler.encode_token(
        user_existing_object.id, user_data.email
    )
    return {"token": auth_token}
