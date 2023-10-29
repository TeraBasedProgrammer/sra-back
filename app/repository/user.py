from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.orm import joinedload, load_only

from app.config.logs.logger import logger
from app.models.db.users import User
from app.models.schemas.users import (UserCreate, UserSchema,
                                      UserUpdateRequest)
from app.repository.base import BaseRepository
from app.utilities.formatters.get_args import get_args


class UserRepository(BaseRepository):
    """Data Access Layer for operating user info"""

    model = User

    async def _get_user_data(self, sql_query) -> Any:
        logger.debug(f"Received data:\n{get_args()}")

        data = await self.async_session.execute(sql_query)
        result = data.unique().scalar_one_or_none()
        return result

    async def create_user(self, user_data: UserCreate) -> Dict[str, Any]:
        logger.debug(f"Received data:\nnew_user_data -> {user_data}")

        new_user: User = await self.create(user_data)

        logger.debug(f"Successfully inserted new user instance into the database")
        return {"id": new_user.id, "email": new_user.email}

    async def create_or_skip(self, user_email: str) -> None:
        """Verifies that user with provided email wasn't registered using login
        and password before and creates new one if wasn't"""

        logger.info("Verifying user registration type")
        user_existing_object = await self.get_user_by_email(user_email)
        if not user_existing_object:
            logger.info(
                "User with provided email hasn't been registered yet, creating new instance"
            )
            new_user = await self.create(
                user_data=UserCreate(
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

    async def get_users(self) -> List[User]:
        result = await self.async_session.execute(
            select(User).options(joinedload(User.companies))
        )
        return result.unique().scalars().all()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result: Optional[User] = await self._get_user_data(
            select(User)
            .options(joinedload(User.tags), joinedload(User.companies))
            .where(User.id == user_id)
        )
        if result:
            logger.debug(f'Retrieved user by id "{user_id}": "{result.id}"')
        return result

    async def get_user_by_email(self, email: EmailStr) -> Optional[User]:
        result: Optional[User] = await self._get_user_data(
            select(User).options(joinedload(User.companies)).where(User.email == email)
        )
        if result:
            logger.debug(f'Retrieved user by email "{email}": "{result.id}"')
        return result

    async def get_user_id(self, email: EmailStr) -> Optional[int]:
        result: Optional[User] = await self._get_user_data(
            select(User).options(load_only(User.id)).where(User.email == email)
        )
        if result:
            logger.debug(f'Retrieved user id by email "{email}": "{id}"')
        return result

    async def exists_by_id(self, user_id: int):
        query = select(User).where(User.id == user_id)
        return await self.exists(query)

    async def exists_by_email(self, email: EmailStr):
        query = select(User).where(User.email == email)
        return await self.exists(query)

    async def update_user(
        self, user_id: int, user_data: UserUpdateRequest
    ) -> Optional[UserSchema]:
        logger.debug(f"Received data:\nuser_data -> {user_data}")
        updated_user = await self.update(
            user_data
        )

        logger.debug(f'Successfully updatetd user instance "{user_id}"')
        return updated_user

    async def delete_user(self, user_id: int) -> Optional[int]:
        logger.debug(f'Received data:\nuser_id -> "{user_id}"')
        result = await self.delete(user_id)

        logger.debug(f'Successfully deleted user "{result}" from the database')
        return result
