from typing import Any

from fastapi import status

from app.utilities.formatters.http_error import validation_error_wrapper


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
                    "example": {
                        "detail": validation_error_wrapper(
                            "Password has incorrect format", "password"
                        )
                    }
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
            "description": "Field validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": validation_error_wrapper(
                            "Invalid password", "password"
                        )
                    }
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


def get_forgot_password_responses() -> dict[int, Any]:
    responses: dict[int, Any] = {
        status.HTTP_400_BAD_REQUEST: {
            "description": "Field validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": validation_error_wrapper(
                            "User with this email is not registered in the system",
                            "email",
                        )
                    }
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


def get_verify_code_responses() -> dict[int, Any]:
    responses: dict[int, Any] = {
        status.HTTP_200_OK: {
            "description": "Succsessful response",
            "content": {"application/json": {"example": {"status": "Valid"}}},
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Field validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": validation_error_wrapper("Invalid code", "code")
                    }
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
                                "loc": ["body", "code"],
                                "msg": "Field required",
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


def get_forgot_password_reset_responses() -> dict[int, Any]:
    responses: dict[int, Any] = {
        status.HTTP_200_OK: {
            "description": "Succsessful response",
            "content": {
                "application/json": {
                    "example": {"status": "The password was successfully changed"}
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Field validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": validation_error_wrapper(
                            "Invalid password", "new_password"
                        )
                    }
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
                                "loc": ["body", "code"],
                                "msg": "Field required",
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
