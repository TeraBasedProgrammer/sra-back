import re
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status

from app.config.logs.logger import logger
from app.utilities.formatters.http_error import error_wrapper
from app.utilities.validators.payload.string_stripper import string_stripper


@string_stripper
def validate_text(
    value: str,
    field_name: str,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
):
    if value is None:
        return value

    if min_length and max_length:
        if not min_length <= len(value) <= max_length:
            logger.warning(f"Validation error: {field_name} has invalid length")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_wrapper(
                    f"{field_name} should contain from {min_length} to {max_length} characters",
                    field_name,
                ),
            )

    if not re.compile(r"^[a-zA-Z0-9\-./!,\(\) ]+$").match(value):
        logger.warning(
            f"Validation error: {field_name} field contains restricted characters"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_wrapper(
                "This field may contain only english letters, numbers and special characters (.-'!()/ )",
                field_name,
            ),
        )

    return value


@string_stripper
def validate_question_temp_uuid(value: str) -> str:
    try:
        UUID(value)
        return value
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_wrapper(
                (
                    "One of the questions has invalid temp UUID field. Ensure you provided valid UUID "
                    "(aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee) for each question"
                ),
                "question_temp_uuid",
            ),
        )
