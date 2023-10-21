from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.repository.user import UserRepository
from app.config.settings.base import settings
from app.api.dependencies.repository import get_repository
from app.api.dependencies.session import get_async_session


class Auth0TokenValidator:
    """Auth0 token verification class"""

    def __init__(self, token: str) -> None:
        self.token: str = token

        # This gets the JWKS from a given URL and does processing so you can
        # use any of the keys available
        jwks_url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    async def verify(self) -> Optional[Dict[str, bool]]:
        # This gets the 'kid' from the passed token
        try:
            self.signing_key = self.jwks_client.get_signing_key_from_jwt(self.token).key
        except jwt.exceptions.PyJWKClientError:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
            )
        except jwt.exceptions.DecodeError:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, detail="Token decode error"
            )

        try:
            payload = jwt.decode(
                self.token,
                self.signing_key,
                algorithms=settings.AUTH0_ALGORITHMS,
                audience=settings.AUTH0_API_AUDIENCE,
                issuer=settings.AUTH0_ISSUER,
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token or its signature has expired",
            )

        # Get user id (or None if user is not registered yet)
        return {"email": payload["email"], "id": None, "auth0": True}


class AuthHandler:
    def __init__(self) -> None:
        self.security = HTTPBearer()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret: str = settings.JWT_SECRET

    async def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password, scheme="bcrypt")

    async def encode_token(self, user_email: str, session: AsyncSession) -> str:
        # Initialize user_crud object to get user id once and put it in jwt payload
        user_crud = get_repository(UserRepository)
        user = await user_crud.get_user_by_email(user_email)

        payload = {
            "exp": datetime.utcnow() + timedelta(days=0, hours=2),
            "iat": datetime.utcnow(),
            "sub": user_email,
            "id": user.id,
        }
        return jwt.encode(payload, self.secret, algorithm="HS256")

    async def decode_token(self, token: str) -> Optional[Dict[str, bool]]:
        try:
            payload = jwt.decode(token, self.secret, algorithms=["HS256"])
            return {"email": payload["sub"], "id": payload["id"], "auth0": False}
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, detail="Signature has expired"
            )
        except jwt.InvalidTokenError as e:
            # If token doesn't have the default structure, 
            # funcion delegates token verification to the auth0 jwt validator
            auth0_decoder = Auth0TokenValidator(token)
            decoded_data = await auth0_decoder.verify()
            if decoded_data:
                return decoded_data
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


class AuthWrapper:
    def __init__(self) -> None:
        self.auth_handler = AuthHandler()

    async def get_payload(
        self,
        session: AsyncSession = Depends(get_async_session),
        auth: HTTPAuthorizationCredentials = Security(settings.jwt_secret),
    ) -> Optional[Dict[str, bool]]:
        user_data = await self.auth_handler.decode_token(auth.credentials, session)

        # Check if there are no registered users to this email address
        if user_data["auth0"]:
            user_crud = get_repository(UserRepository)
            new_user: Dict[str, Any] | None = await user_crud.error_or_create(
                user_data["email"]
            )

            # Add new user id to the user_data
            if new_user:
                user_data["id"] = new_user["id"]
                return user_data

        return user_data


auth_wrapper = AuthWrapper()
