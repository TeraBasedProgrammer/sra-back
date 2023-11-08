import uuid

from fastapi import HTTPException, status
from pydantic import EmailStr

from app.config.logs.logger import logger
from app.config.settings.base import settings
from app.core.database import redis
from app.core.tasks import send_email_report_dashboard
from app.models.db.users import User
from app.models.schemas.auth import (
    UserLoginInput,
    UserLoginOutput,
    UserSignUpInput,
    UserSignUpOutput,
)
from app.models.schemas.company_user import UserFullSchema
from app.models.schemas.users import (
    PasswordChangeOutput,
    PasswordResetInput,
    UserCreate,
    UserUpdate,
)
from app.repository.user import UserRepository
from app.securities.authorization.auth_handler import auth_handler
from app.services.base import BaseService
from app.utilities.formatters.http_error import error_wrapper


class UserService(BaseService):
    def __init__(self, user_repository) -> None:
        self.user_repository: UserRepository = user_repository

    async def register_user(self, user_data: UserSignUpInput) -> UserSignUpOutput:
        logger.info("Creating new User instance")

        user_existing_object = await self.user_repository.exists_by_email(
            user_data.email
        )
        if user_existing_object:
            logger.warning(f'User with email "{user_data.email}" already exists')
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

        # Hashing input password
        user_data.password = auth_handler.get_password_hash(user_data.password)
        result = await self.user_repository.create_user(
            UserCreate(**user_data.model_dump())
        )

        logger.info("New user instance has been successfully created")
        return result

    async def authenticate_user(self, user_data: UserLoginInput) -> UserLoginOutput:
        logger.info(f'Login attempt with email "{user_data.email}"')

        user_existing_object = await self.user_repository.get_user_by_email(
            user_data.email
        )
        if not user_existing_object:
            logger.warning(
                f'User with email "{user_data.email}" is not registered in the system'
            )
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="User with this email is not registered in the system",
            )

        verify_password = auth_handler.verify_password(
            user_data.password, user_existing_object.password
        )
        if not verify_password:
            logger.warning("Invalid password was provided")
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=error_wrapper("Invalid password", "password"),
            )

        logger.info(f'User "{user_data.email}" successfully logged in the system')
        auth_token = auth_handler.encode_token(user_existing_object.id, user_data.email)
        return {"token": auth_token}

    async def get_user_profile(self, current_user: User) -> UserFullSchema:
        logger.info("Successfully returned current user info")

        return UserFullSchema.from_model(current_user)

    async def update_user_profile(
        self, current_user: User, data: UserUpdate
    ) -> UserFullSchema:
        logger.info(f'Updating user profile of the user "{current_user}"')

        # Validate if data was provided
        new_fields = data.model_dump(exclude_none=True)
        if new_fields == {}:
            logger.warning("Validation error: No parameters have been provided")
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=error_wrapper(
                    "At least one valid field should be provided", None
                ),
            )

        updated_user = await self.user_repository.update_user(current_user.id, data)

        logger.info(f'"{current_user}" profile was successfully updated')
        return await self.get_user_profile(updated_user)

    async def reset_password(
        self, current_user: User, data: PasswordResetInput
    ) -> PasswordChangeOutput:
        logger.info(f'Change password request from user "{current_user}"')

        # Validate the old password match the current one
        if not auth_handler.verify_password(data.old_password, current_user.password):
            logger.warning("Invalid old password was provided")
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=error_wrapper("Invalid old password", "old_password"),
            )

        # Validate the new password does not match the old password
        if auth_handler.verify_password(data.new_password, current_user.password):
            logger.warning("Error: New password and old password are the same")
            raise HTTPException(
                status.HTTP_409_CONFLICT, detail="You can't use your old password"
            )

        current_user.password = auth_handler.get_password_hash(data.new_password)

        await self.user_repository.save(current_user)
        logger.info("The password was successfully updated")

        return PasswordChangeOutput(message="The password was successfully reset")

    async def handle_forgot_password(self, user_email: str) -> PasswordChangeOutput:
        if not await self.user_repository.exists_by_email(user_email):
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=error_wrapper("User with this email is not found", "email"),
            )

        user: User = await self.user_repository.get_user_by_email(user_email)
        user_name: str = "User" if not user else user.name

        # Generate password reset link
        reset_code = str(uuid.uuid1())
        reset_link = f"{settings.FRONT_HOST}:{settings.FRONT_PORT}/forgot_password/reset/?q={reset_code}"

        # Put reset link into Redis
        await redis.set(reset_code, f"reset-key-{user_email}", ex=3600)
        # Create a background task to send an email
        send_email_report_dashboard.delay(user_email, user_name, reset_link)

        return PasswordChangeOutput(
            message="A link to reset your password has been sent to your email"
        )

    async def verify_code(self, code: str) -> dict[str, str]:
        if not await redis.get(code):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=error_wrapper("Invalid code", "code"),
            )

        return {"status": "Valid"}

    async def reset_forgotten_password(
        self, new_password: str, code: str
    ) -> dict[str, str]:
        await self.verify_code(code)

        user_email: EmailStr = (await redis.get(code)).split("-")[-1]
        user_to_update = await self.user_repository.get_user_by_email(user_email)

        user_to_update.password = auth_handler.get_password_hash(new_password)

        await self.user_repository.save(user_to_update)
        logger.info("The password was successfully updated")

        return {"status": "The password was successfully changed"}
