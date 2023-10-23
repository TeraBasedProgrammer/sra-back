import jwt
from fastapi import HTTPException, status

from app.config.settings.base import settings


class Auth0TokenValidator:
    """Auth0 token verification class"""

    def __init__(self, token: str) -> None:
        self.token: str = token

        # This gets the JWKS from a given URL and does processing so you can
        # use any of the keys available
        jwks_url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    async def verify(self) -> dict[str, bool]:
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


def get_auth0_token_validator(token: str) -> Auth0TokenValidator:
    return Auth0TokenValidator(token)
