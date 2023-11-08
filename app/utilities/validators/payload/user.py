import re

from fastapi import HTTPException, status

from app.config.logs.logger import logger
from app.utilities.formatters.http_error import error_wrapper


def validate_password(value: str, field_name: str = "password"):
    if not re.compile(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$").match(value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_wrapper(
                "Password should contain at least eight characters, at least one letter and one number",
                field_name,
            ),
        )
    return value


def validate_name(value: str):
    if not value:
        return value
    if not re.compile(r"^[a-zA-Z\- ]+$").match(value):
        logger.warning("Validation error: 'name' field contains restricted characters")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_wrapper("Name should contain only english letters", "name"),
        )
    return value


def validate_phone_number(value: str):
    if not value:
        return value
    if value[0] != "+":
        logger.warning(
            "Validation error: 'phone_number' field does not contain '+' character "
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_wrapper(
                "Phone number should start with '+' character", "phone_number"
            ),
        )
    return value
