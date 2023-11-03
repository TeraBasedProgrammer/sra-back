from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.config.logs.logger import logger
from app.models.db.users import User
from app.models.schemas.users import UserCreate, UserUpdate
from app.repository.base import BaseRepository
from app.utilities.formatters.get_args import get_args


class UserRepository(BaseRepository):
    """Data Access Layer for operating user info"""

    model = User

    async def create_user(self, user_data: UserCreate) -> Dict[str, Any]:
        logger.debug(f"Received data:\n{get_args(1)}")

        new_user: User = await self.create(user_data)

        logger.debug("Successfully inserted new user instance into the database")
        return {"id": new_user.id, "email": new_user.email}

    async def create_or_skip(self, user_email: str) -> None:
        """Verifies that user with provided email wasn't registered using login
        and password before and creates new one if wasn't"""
        logger.debug(f"Received data:\n{get_args()}")

        logger.info("Verifying user registration type")
        user_existing_object = await self.exists_by_email(user_email)
        if not user_existing_object:
            logger.info(
                "User with provided email hasn't been registered yet, creating new instance"
            )
            new_user: User = await self.create(
                UserCreate(
                    email=user_email,
                    password=f"pass{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    name=None,
                    auth0_registered=True,
                )
            )
            return {"id": new_user.id, "email": new_user.email}
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
        logger.debug(f"Received data:\n{get_args()}")

        query = (
            select(User)
            .options(joinedload(User.tags), joinedload(User.companies))
            .where(User.id == user_id)
        )
        result: Optional[User] = await self.get_instance(query)
        if result:
            logger.debug(f'Retrieved user by id "{user_id}": "{result.id}"')
        return result

    async def get_user_by_email(self, email: EmailStr) -> Optional[User]:
        logger.debug(f"Received data:\n{get_args()}")

        query = (
            select(User)
            .options(joinedload(User.tags), joinedload(User.companies))
            .where(User.email == email)
        )
        result: Optional[User] = await self.get_instance(query)
        if result:
            logger.debug(f'Retrieved user by email "{email}": "{result.id}"')
        return result

    # TODO: test
    async def get_user_id(self, email: EmailStr) -> Optional[int]:
        logger.debug(f"Received data:\n{get_args()}")

        query = select(User).where(User.email == email).with_only_columns(User.id)
        result: Optional[User] = await self.get_instance(query)
        if result:
            logger.debug(f'Retrieved user id by email "{email}": "{result.id}"')
        return result

    async def exists_by_id(self, user_id: int) -> bool:
        logger.debug(f"Received data:\n{get_args()}")

        query = select(User).where(User.id == user_id)
        return await self.exists(query)

    async def exists_by_email(self, email: EmailStr) -> bool:
        logger.debug(f"Received data:\n{get_args()}")

        query = select(User).where(User.email == email)
        return await self.exists(query)

    # TODO: test
    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        logger.debug(f"Received data:\n{get_args()}")
        updated_user = await self.update(user_id, user_data)

        logger.debug(f'Successfully updatetd user instance "{user_id}"')
        return updated_user

    # TODO: test
    async def delete_user(self, user_id: int) -> Optional[int]:
        logger.debug(f"Received data:\n{get_args()}")
        result = await self.delete(user_id)

        logger.debug(f'Successfully deleted user "{result}" from the database')
        return result
