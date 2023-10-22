import pathlib

from pydantic_settings import BaseSettings
import decouple


ROOT_DIR = pathlib.Path(__file__).parent.parent.parent.parent.resolve()


class BackendBaseSettings(BaseSettings):
    DEBUG: bool = decouple.config("DEBUG", cast=bool)
    LOGGING_LEVEL: str = decouple.config("LOGGING_LEVEL") 
    REDIS_URL: str = decouple.config("REDIS_URL") 
    JWT_SECRET: str = decouple.config("JWT_SECRET") 
    AUTH0_DOMAIN: str = decouple.config("AUTH0_DOMAIN") 
    AUTH0_API_AUDIENCE: str = decouple.config("AUTH0_API_AUDIENCE") 
    AUTH0_ALGORITHMS: str = decouple.config("AUTH0_ALGORITHMS") 
    AUTH0_ISSUER: str = decouple.config("AUTH0_ISSUER")  
    POSTGRES_USER: str = decouple.config("POSTGRES_USER") 
    POSTGRES_PASSWORD: str = decouple.config("POSTGRES_PASSWORD") 
    POSTGRES_DB: str = decouple.config("POSTGRES_DB") 
    POSTGRES_PORT: int = decouple.config("POSTGRES_PORT", cast=int) 
    POSTGRES_HOST: str = decouple.config("POSTGRES_HOST") 
    IS_ALLOWED_CREDENTIALS: bool = decouple.config("IS_ALLOWED_CREDENTIALS", cast=bool) 

    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",  # React default port
        "http://0.0.0.0:3000",
        "http://127.0.0.1:3000",  # React docker port
        "http://127.0.0.1:3001",
        "http://localhost:5173",  # Qwik default port
        "http://0.0.0.0:5173",
        "http://127.0.0.1:5173",  # Qwik docker port
        "http://127.0.0.1:5174",
    ]
    ALLOWED_METHODS: list[str] = ["*"]
    ALLOWED_HEADERS: list[str] = ["*"]

    class Config:
        # env_file = f"{ROOT_DIR}/.env"
        env_file = None


settings = BackendBaseSettings()
