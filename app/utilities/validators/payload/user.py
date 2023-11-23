import re

from fastapi import HTTPException, status

from app.config.logs.logger import logger
from app.utilities.formatters.http_error import error_wrapper
from app.utilities.validators.payload.string_stripper import string_stripper


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


@string_stripper
def validate_name(value: str):
    if value is None:
        return value
    if not (2 <= len(value) <= 25):
        logger.warning("Validation error: 'name' has invalid length")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_wrapper("Name should contain from 2 to 25 characters", "name"),
        )

    if not re.compile(r"^[a-zA-Z\- ]+$").match(value):
        logger.warning("Validation error: 'name' field contains restricted characters")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_wrapper("Name should contain only english letters", "name"),
        )
    return value


@string_stripper
def validate_phone_number(value: str):
    if value is None:
        return value
    if not (8 <= len(value[1:]) <= 20):
        logger.warning("Validation error: 'phone_number' has invalid length")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_wrapper(
                "Phone number should contain from 8 to 20 characters", "phone_number"
            ),
        )
    if value[0] != "+" or not re.compile(r"^[0-9]+$").match(value[1:]):
        logger.warning(
            "Validation error: 'phone_number' field does not contain '+' character or contains incorrect characters"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_wrapper(
                "Phone number should start with '+' and contain only numeric characters (0-9)",
                "phone_number",
            ),
        )
    return value
