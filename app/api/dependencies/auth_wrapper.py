from typing import Optional

from fastapi import Security, Depends
from fastapi.security import HTTPAuthorizationCredentials

from app.config.settings.base import settings
from app.securities.authorization.auth_handler import auth_handler, AuthHandler
from app.utilities.db.user_actions import create_user_or_skip


async def auth_wrapper(
        auth: HTTPAuthorizationCredentials = Security(settings.JWT_SECRET),
        auth_handler: AuthHandler = Depends(auth_handler)
    ) -> Optional[dict[str, bool]]:
        user_data = await auth_handler.decode_token(auth.credentials)

        # Create new user (or skip if it exists) if token is received from Auth0
        if user_data["auth0"]:
            new_user_data = await create_user_or_skip(user_data)
            if new_user_data:
                return new_user_data

        return user_data