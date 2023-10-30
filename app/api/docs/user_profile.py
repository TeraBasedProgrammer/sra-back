from typing import Any

from fastapi import status


def get_profile_responses() -> dict[int, Any]:
    responses: dict[int, Any] = (
        {
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Token decode error or token was not provided",
                "content": {
                    "application/json": {"example": {"detail": "Not authenticated"}}
                },
            },
        }
    )

    return responses
