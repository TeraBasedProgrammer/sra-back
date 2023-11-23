from datetime import datetime

from fastapi import HTTPException, status

from app.utilities.formatters.http_error import error_wrapper


def validate_date_format(value: str, field_name: str):
    if value is None:
        return value

    try:
        # Raises ValueError if format is incorrect
        _ = datetime.strptime(value, "%d-%m-%Y")
    except ValueError:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=error_wrapper(
                "Incorrect date format. Should be 'DD-MM-YYYY'", field_name
            ),
        )

    return value


def validate_time_format(value: str, field_name: str):
    if value is None:
        return value

    try:
        # Raises ValueError if format is incorrect
        _ = datetime.strptime(value, "%H:%M")
    except ValueError:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=error_wrapper(
                "Incorrect time format. Should be 'HH:MM'", field_name
            ),
        )

    return value
