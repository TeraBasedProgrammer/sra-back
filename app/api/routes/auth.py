from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.repository import get_repository
from app.api.dependencies.services import get_user_service
from app.config.logs.logger import logger
from app.models.schemas.auth import (UserLoginInput, UserLoginOutput,
                                     UserSignUpInput, UserSignUpOutput)
from app.repository.user import UserRepository
from app.securities.authorization.auth_handler import auth_handler
from app.services.user import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup/", response_model=UserSignUpOutput, status_code=201)
async def signup(
    user_data: UserSignUpInput, user_service: UserService = Depends(get_user_service)
) -> UserSignUpOutput:
    return await user_service.register_user(user_data)


@router.post("/login/",response_model=UserLoginOutput)
async def login(
    user_data: UserLoginInput, user_service: UserService = Depends(get_user_service)
) -> UserLoginOutput:
    return await user_service.authenticate_user(user_data)
