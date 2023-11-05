import re

from fastapi import HTTPException, status

from app.config.logs.logger import logger
from app.utilities.formatters.http_error import validation_error_wrapper


def validate_text(value: str, field_name: str):
    if not re.compile(r"^[a-zA-Z0-9\-./!,\(\) ]+$").match(value):
        logger.warning(
            f"Validation error: {field_name} field contains restricted characters"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation_error_wrapper(
                "This field may contain only english letters, numbers and special characters (.-'!()/ )",
                field_name,
            ),
        )

    return value
