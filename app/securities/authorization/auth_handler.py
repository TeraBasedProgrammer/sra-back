from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer
from passlib.context import CryptContext
from starlette import status

from app.config.settings.base import settings
from app.securities.authorization.auth0_jwt import get_auth0_token_validator


class AuthHandler:
    def __init__(self) -> None:
        self.security = HTTPBearer()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret: str = settings.JWT_SECRET

    async def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password, scheme="bcrypt")

    async def encode_token(self, user_id: int, user_email: str) -> str:
        # Initialize user_crud object to get user id once and put it in jwt payload

        payload = {
            "exp": datetime.utcnow() + timedelta(days=0, hours=2),
            "iat": datetime.utcnow(),
            "sub": user_email,
            "id": user_id,
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
        except jwt.InvalidTokenError:
            # If token doesn't have the default structure, 
            # funcion delegates token verification to the auth0 jwt validator
            auth0_decoder = get_auth0_token_validator(token)
            decoded_data = await auth0_decoder.verify()
            if decoded_data:
                return decoded_data
            
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def get_auth_handler() -> AuthHandler:
    return AuthHandler()

auth_handler: AuthHandler = get_auth_handler()
