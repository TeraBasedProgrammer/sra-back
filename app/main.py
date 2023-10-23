import logging
import logging.config

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check

from app.api.endpoints import router
from app.config.logs.log_config import LOGGING_CONFIG
from app.config.settings.base import settings

# Set up logging configuration
logging.config.dictConfig(LOGGING_CONFIG)

app = FastAPI()
app.include_router(router)

# Enable pagination in the app
add_pagination(app)
disable_installed_extensions_check()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.IS_ALLOWED_CREDENTIALS,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)
