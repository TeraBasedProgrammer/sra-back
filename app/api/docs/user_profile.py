from typing import Any

from fastapi import status

from app.utilities.formatters.http_error import validation_error_wrapper


def get_profile_responses() -> dict[int, Any]:
    responses: dict[int, Any] = {
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token decode error or token was not provided",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated"}}
            },
        },
    }

    return responses


def get_reset_password_responses() -> dict[int, Any]:
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
                            "Invalid old password", "old_password"
                        )
                    }
                }
            },
        },
        status.HTTP_409_CONFLICT: {
            "description": "The new password matches the old one",
            "content": {
                "application/json": {"example": {"detail": "Matching passwords"}}
            },
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "One or more fields were passed incorrectly | Field validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "string_type",
                                "loc": ["body", "old_password"],
                                "msg": "Input should be a valid string",
                                "input": 0,
                                "url": "https://errors.pydantic.dev/2.1.2/v/string_type",
                            }
                        ]
                    }
                }
            },
        },
    }

    return responses


def get_edit_profile_responses() -> dict[int, Any]:
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
                        "detail": validation_error_wrapper("Invalid name", "name")
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
                                "type": "string_type",
                                "loc": ["body", "name"],
                                "msg": "Input should be a valid string",
                                "input": 0,
                                "url": "https://errors.pydantic.dev/2.1.2/v/string_type",
                            }
                        ]
                    }
                }
            },
        },
    }

    return responses


def get_user_companies_responses() -> dict[int, Any]:
    responses: dict[int, Any] = {
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token decode error or token was not provided",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated"}}
            },
        },
    }

    return responses