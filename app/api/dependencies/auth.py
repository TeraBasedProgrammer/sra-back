from typing import Any, Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.dependencies.repository import get_repository
from app.repository.user import UserRepository
from app.securities.authorization.auth_handler import auth_handler
from app.utilities.db.user_actions import create_user_or_skip


async def auth_wrapper(
    auth: HTTPAuthorizationCredentials = Security(HTTPBearer(auto_error=False)),
    user_repository=Depends(get_repository(UserRepository)),
) -> Optional[dict[str, Any]]:
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    user_data = await auth_handler.decode_token(auth.credentials)

    # Create new user (or skip if it exists) if token is received from Auth0
    if user_data["auth0"]:
        new_user_data = await create_user_or_skip(user_repository, user_data)
        if new_user_data:
            return new_user_data

    return user_data
