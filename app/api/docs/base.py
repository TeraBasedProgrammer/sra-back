from typing import Any, Optional

from app.utilities.formatters.http_error import validation_error_wrapper


class ResponseDocumentation:
    def _400_response(
        self,
        error_text: str,
        error_field: Optional[str],
        description: str = "Field validation error",
    ) -> dict[str, Any]:
        return {
            "description": description,
            "content": {
                "application/json": {
                    "example": {
                        "detail": validation_error_wrapper(error_text, error_field)
                    }
                }
            },
        }

    def _401_response(
        self,
        description: str = "Token decode error or token was not provided",
        example: dict[Any] = {"detail": "Not authenticated"},
    ) -> dict[str, Any]:
        return {
            "description": description,
            "content": {"application/json": {"example": example}},
        }

    def _403_response(
        self,
        description: str = "Permission error",
        example: dict[Any] = {"detail": "Forbidden"},
    ) -> dict[str, Any]:
        return {
            "description": description,
            "content": {"application/json": {"example": example}},
        }

    def _404_response(
        self,
        description: str = "Not found",
        example: dict[Any] = {"detail": "Not found"},
    ) -> dict[str, Any]:
        return {
            "description": description,
            "content": {"application/json": {"example": example}},
        }

    def _409_response(self, description: str, example: dict[Any]) -> dict[dict, Any]:
        return {
            "description": description,
            "content": {"application/json": {"example": example}},
        }

    def _422_response(
        self,
        loc: list[str],
        msg: str,
        description: str = "One or more fields were passed incorrectly | Field validation error",
    ) -> dict[str, Any]:
        return {
            "description": description,
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "error_type",
                                "loc": loc,
                                "msg": msg,
                                "input": "user input",
                                "url": "error docs url",
                            }
                        ]
                    }
                }
            },
        }
