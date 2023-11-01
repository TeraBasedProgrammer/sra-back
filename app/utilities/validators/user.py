import re

from fastapi import HTTPException, status

from app.config.logs.logger import logger


def validate_password(value: str):
    if not re.compile(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$").match(value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password should contain at least eight characters, at least one letter and one number",
        )
    return value


def validate_name(value: str):
    if not value:
        return value
    if not re.compile(r"^[a-zA-Z\- ]+$").match(value):
        logger.warning("Validation error: 'name' field contains restricted characters")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name should contain only english letters",
        )
    return value
