from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api.dependencies.repository import get_repository
from app.config.logs.logger import logger
from app.models.db.companies import Company, CompanyUser
from app.models.db.quizzes import Quiz
from app.models.db.users import User
from app.models.schemas.auth import UserSignUpAuth0, UserSignUpInput
from app.models.schemas.users import (UpdateUserScore, UserSchema,
                                      UserUpdateRequest)
from app.repository.base import BaseRepository
from app.securities.authorization.auth_handler import auth_handler
from app.utilities.db.model_crud import (create_model_instance,
                                         delete_model_instance,
                                         update_model_instance)
from app.utilities.formatters.error_wrapper import error_wrapper


class UserRepository(BaseRepository):
    """Data Access Layer for operating user info"""

    async def create_user(
        self, user_data: UserSignUpInput, auth0: bool = False
    ) -> Dict[str, Any]:
        logger.debug(f"Received data:\nnew_user_data -> {user_data}")
        new_user = await create_model_instance(self.async_session, User, user_data)

        new_user.password = await auth_handler.get_password_hash(new_user.password)
        new_user.companies = []
        logger.debug(f'Enctypted the password: "{new_user.password[:10]}..."')

        if auth0:
            new_user.auth0_registered = True

        await self.async_session.commit()
        logger.debug(f"Successfully inserted new user instance into the database")
        return {"id": new_user.id, "email": new_user.email}

    async def get_users(self) -> List[User]:
        result = await self.async_session.execute(
            select(User).options(joinedload(User.companies))
        )
        return result.unique().scalars().all()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        logger.debug(f'Received data:\nuser_id -> "{user_id}"')
        data = await self.async_session.execute(
            select(User).options(joinedload(User.companies)).where(User.id == user_id)
        )
        result = data.unique().scalar_one_or_none()
        if result:
            logger.debug(f'Retrieved user by id "{user_id}": "{result.email}"')
        return result

    async def get_user_by_email(self, email: EmailStr) -> Optional[User]:
        logger.debug(f'Received data:\nuser_email -> "{email}"')
        data = await self.async_session.execute(
            select(User).options(joinedload(User.companies)).where(User.email == email)
        )
        result = data.unique().scalar_one_or_none()
        if result:
            logger.debug(f'Retrieved user by email "{email}": "{result.id}"')
        return result

    async def update_user(
        self, user_id: int, user_data: UserUpdateRequest
    ) -> Optional[UserSchema]:
        logger.debug(f"Received data:\nuser_data -> {user_data}")
        updated_user = await update_model_instance(
            self.async_session, User, user_id, user_data
        )

        logger.debug(f'Successfully updatetd user instance "{user_id}"')
        return updated_user

    async def delete_user(self, user_id: int) -> Optional[int]:
        logger.debug(f'Received data:\nuser_id -> "{user_id}"')
        result = await delete_model_instance(self.async_session, User, user_id)

        logger.debug(f'Successfully deleted user "{result}" from the database')
        return result

    async def create_or_skip(self, user_email: str) -> None:
        """Verifies that user with provided email wasn't registered using login
        and password before and creates new one if wasn't"""
        logger.info("Verifying user registration type")
        user_existing_object = await self.get_user_by_email(user_email)
        if not user_existing_object:
            logger.info(
                "User with provided email hasn't been registered yet, creating new instance"
            )
            new_user = await self.create_user(
                user_data=UserSignUpAuth0(
                    email=user_email,
                    password=f"pass{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    auth0_registered=True,
                )
            )
            return new_user
        else:
            logger.info(
                "User with provided email has been registered using Auth0, pass"
            )
            return


user_repository: UserRepository = get_repository(UserRepository)
