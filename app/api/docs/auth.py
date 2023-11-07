from fastapi import status

from app.api.docs.base import ResponseDocumentation


class AuthDocumentation(ResponseDocumentation):
    def signup(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            status.HTTP_409_CONFLICT: self._409_response(
                "User email is already registered in the system",
                {"detail": "User with email 'user@example.com' already exists"},
            ),
            status.HTTP_400_BAD_REQUEST: self._400_response(
                "Password has incorrect format", "password"
            ),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["body", "email"], "Input should be a valid string"
            ),
        }

        return responses

    def login(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            status.HTTP_404_NOT_FOUND: self._404_response(
                example={
                    "detail": "User with this email is not registered in the system"
                }
            ),
            status.HTTP_400_BAD_REQUEST: self._400_response(
                "Invalid password", "password"
            ),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["body", "email"], "Input should be a valid string"
            ),
        }

        return responses

    def forgot_password(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            status.HTTP_400_BAD_REQUEST: self._400_response(
                "User with this email is not registered in the system", "email"
            ),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["body", "email"], "Input should be a valid string"
            ),
        }

        return responses

    def verify_reset_password_code(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            status.HTTP_200_OK: {
                "description": "Succsessful response",
                "content": {"application/json": {"example": {"status": "Valid"}}},
            },
            status.HTTP_400_BAD_REQUEST: self._400_response("Invalid code", "code"),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["body", "code"], "Field required"
            ),
        }

        return responses

    def reset_forgotten_password(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            status.HTTP_200_OK: {
                "description": "Succsessful response",
                "content": {
                    "application/json": {
                        "example": {"status": "The password was successfully changed"}
                    }
                },
            },
            status.HTTP_400_BAD_REQUEST: self._400_response(
                "Invalid password", "new_password"
            ),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["body", "code"], "Field required"
            ),
        }

        return responses


auth_docs = AuthDocumentation()
