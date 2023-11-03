from typing import Any

from fastapi import status

from app.utilities.formatters.http_error import validation_error_wrapper


def get_create_company_responses() -> dict[int, Any]:
    responses: dict[int, Any] = {
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token decode error or token was not provided",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated"}}
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Field validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": validation_error_wrapper(
                            "This field may contain only english letters, numbers and special characters (.-'!()/ )",
                            "title",
                        )
                    }
                }
            },
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "One or more fields were passed incorrectly",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "string_too_long",
                                "loc": ["body", "title"],
                                "msg": "String should have at most 25 characters",
                                "input": "Very long company title Very long company title",
                                "ctx": {"max_length": 25},
                                "url": "https://errors.pydantic.dev/2.1.2/v/string_too_long",
                            }
                        ]
                    }
                }
            },
        },
    }

    return responses


def get_get_company_responses() -> dict[int, Any]:
    responses: dict[int, Any] = {
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token decode error or token was not provided",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated"}}
            },
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not found",
            "content": {
                "application/json": {"example": {"detail": "Company is not found"}}
            },
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "One or more fields were passed incorrectly | Field validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "int_parsing",
                                "loc": ["path", "company_id"],
                                "msg": "Input should be a valid integer, unable to parse string as an integer",
                                "input": "not_an_integer",
                                "url": "https://errors.pydantic.dev/2.1.2/v/int_parsing",
                            }
                        ]
                    }
                }
            },
        },
    }

    return responses