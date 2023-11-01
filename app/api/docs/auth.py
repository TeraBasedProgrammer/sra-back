from typing import Any

from fastapi import status


def get_signup_responses() -> dict[int, Any]:
    responses: dict[int, Any] = {
        status.HTTP_409_CONFLICT: {
            "description": "User email is already registered in the system",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "User with email 'user@example.com' already exists"
                    }
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Input password has incorrect format",
            "content": {
                "application/json": {
                    "example": {"detail": "Password has incorrect format"}
                }
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
                                "loc": ["body", "email"],
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


def get_login_responses() -> dict[int, Any]:
    responses: dict[int, Any] = {
        status.HTTP_404_NOT_FOUND: {
            "description": "User email is not registered in the system",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "User with this email is not registered in the system"
                    }
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid password",
            "content": {
                "application/json": {"example": {"detail": "Invalid password"}}
            },
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "One or more fields were passed incorrectl | Field validation errory",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "string_type",
                                "loc": ["body", "email"],
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
