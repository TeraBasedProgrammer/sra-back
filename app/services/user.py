from fastapi import HTTPException, status

from app.config.logs.logger import logger
from app.models.db.users import User
from app.models.schemas.auth import (UserLoginInput, UserLoginOutput,
                                     UserSignUpInput, UserSignUpOutput)
from app.models.schemas.company_user import UserFullSchema
from app.models.schemas.users import (PasswordResetInput, PasswordResetOutput,
                                      UserCreate, UserUpdate)
from app.repository.user import UserRepository
from app.securities.authorization.auth_handler import auth_handler


class UserService:
    def __init__(self, user_repository) -> None:
        self.user_repository: UserRepository = user_repository

    async def register_user(self, user_data: UserSignUpInput) -> UserSignUpOutput:
        logger.info(f"Creating new User instance")

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
        user_data.password = await auth_handler.get_password_hash(user_data.password)
        result = await self.user_repository.create_user(
            UserCreate(**user_data.model_dump())
        )

        logger.info(f"New user instance has been successfully created")
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
            logger.warning(f"Invalid password was provided")
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid password")

        logger.info(f'User "{user_data.email}" successfully logged in the system')
        auth_token = auth_handler.encode_token(user_existing_object.id, user_data.email)
        return {"token": auth_token}

    async def get_user_profile(self, current_user: User) -> UserFullSchema:
        logger.info(f"Successfully returned current user info")

        return await UserFullSchema.from_model(current_user)

    async def update_user_profile(
        self, current_user: User, data: UserUpdate
    ) -> UserFullSchema:
        logger.info(f'Updating user profile of the user "{current_user}"')

        updated_user = await self.user_repository.update_user(current_user.id, data)

        logger.info(f'"{current_user}" profile was successfully updated')
        return await self.get_user_profile(updated_user)

    async def reset_password(
        self, current_user: User, data: PasswordResetInput
    ) -> PasswordResetOutput:
        logger.info(f'Change password request from user "{current_user}"')

        # Validate the old password match the current one
        if not auth_handler.verify_password(data.old_password, current_user.password):
            logger.warning("Invalid old password was provided")
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, detail="Invalid old password"
            )

        # Validate the new password does not match the old password
        if auth_handler.verify_password(data.new_password, current_user.password):
            logger.warning("Error: New password and old password are the same")
            raise HTTPException(
                status.HTTP_409_CONFLICT, detail="You can't use your old password"
            )

        current_user.password = auth_handler.get_password_hash(data.new_password)

        await self.user_repository.save(current_user)
        logger.info(f"The password was successfully updated")

        return PasswordResetOutput
