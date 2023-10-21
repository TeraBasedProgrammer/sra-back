from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth_wrapper import auth_wrapper
from app.api.dependencies.repository import get_repository
from app.config.logs.logger import logger
from app.models.schemas.auth import UserLogin, UserSignUp
from app.repository.user import UserRepository
from app.securities.authorization.auth_handler import auth_handler
from app.utilities.formatters.error_wrapper import error_wrapper

router = APIRouter(
    prefix="/auth", tags=["Auth"], responses={404: {"description": "Not found"}}
)


# @router.get(
#     path="/me/", response_model=Optional[UserFullSchema], response_model_exclude_none=True
# )
# async def get_current_user(
#     session: AsyncSession = Depends(get_async_session),
#     auth=Depends(auth_wrapper.get_payload),
# ) -> Optional[UserFullSchema]:
#     logger.info(f"Accessing current user info")
#     crud = UserRepository(session)

#     current_user = await crud.get_user_by_email(auth["email"])

#     logger.info(f"Successfully returned current user info")
#     return await UserFullSchema.from_model(current_user, public_request=False)


# @router.get("/me/attempts/", response_model=list[AttemptListResponseModel])
# async def get_all_attempts(
#     session: AsyncSession = Depends(get_async_session),
#     auth=Depends(auth_handler.auth_wrapper),
# ) -> list[AttemptListResponseModel]:
#     logger.info(f"Retrieving current user attempts")

#     # Initialize services
#     attempt_crud = AttemptRepository(session)

#     # Retrieving current user id
#     current_user_id = await get_current_user_id(session, auth)

#     res = await attempt_crud.get_user_attempts(current_user_id)
#     logger.info(f"Successfully retrieved current user attempts")
#     return res


# @router.get("/me/{company_id}/attempts/", response_model=list[AttemptListResponseModel])
# async def get_company_attempts(
#     company_id: int,
#     session: AsyncSession = Depends(get_async_session),
#     auth=Depends(auth_handler.auth_wrapper),
# ) -> list[AttemptListResponseModel]:
#     logger.info(f'Retrieving current user attempts in company "{company_id}"')

#     # Initialize services
#     attempt_crud = AttemptRepository(session)
#     company_crud = CompanyRepository(session)

#     # Retrieving current user id
#     current_user_id = await get_current_user_id(session, auth)

#     request_company = await company_crud.get_company_by_id(
#         company_id, current_user_id, member_only=True
#     )
#     if not request_company:
#         logger.warning(f'Company "{company_id}" is not found')
#         raise HTTPException(
#             status.HTTP_404_NOT_FOUND,
#             detail=error_wrapper("Requested company is not found"),
#         )

#     res = await attempt_crud.get_user_attempts(current_user_id, company_id=company_id)
#     logger.info(
#         f'Successfully retrieved current user attempts in company "{company_id}"'
#     )
#     return res


@router.post("/signup/", response_model=Optional[Dict[str, Any]], status_code=201)
async def signup(
    user: UserSignUp,
    user_crud: UserRepository = Depends(get_repository(UserRepository)),
) -> Optional[Dict[str, str]]:
    logger.info(f"Creating new User instance")

    user_existing_object = await user_crud.get_user_by_email(user.email)
    if user_existing_object:
        logger.warning(
            f'Validation error: User with email "{user.email}" already exists'
        )
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=error_wrapper("User with this email already exists"),
        )
    result = await user_crud.create_user(user)
    logger.info(f"New user instance has been successfully created")
    return result


@router.post("/login/")
async def login(
    user_data: UserLogin,
    user_crud: UserRepository = Depends(get_repository(UserRepository)),
) -> Optional[Dict[str, str]]:
    logger.info(f'Login attempt with email "{user_data.email}"')

    user_existing_object = await user_crud.get_user_by_email(user_data.email)
    if not user_existing_object:
        logger.warning(
            f'User with email "{user_data.email}" is not registered in the system'
        )
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=error_wrapper(
                "User with this email is not registered in the system"
            ),
        )

    verify_password = await auth_handler.verify_password(
        user_data.password, user_existing_object.password
    )
    if not verify_password:
        logger.warning(f"Invalid password was provided")
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail=error_wrapper("Invalid password")
        )
    logger.info(f'User "{user_data.email}" successfully logged in the system')
    auth_token = await auth_handler.encode_token(
        user_existing_object.id, user_data.email
    )
    return {"token": auth_token}
