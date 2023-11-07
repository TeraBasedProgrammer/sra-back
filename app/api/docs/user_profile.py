from fastapi import status

from app.api.docs.base import ResponseDocumentation


class UserProfileDocumentation(ResponseDocumentation):
    def get_user_profile(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            status.HTTP_401_UNAUTHORIZED: self._401_response(),
        }

        return responses

    def get_user_companies(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            status.HTTP_401_UNAUTHORIZED: self._401_response(),
        }

        return responses

    def edit_user_profile(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            status.HTTP_401_UNAUTHORIZED: self._401_response(),
            status.HTTP_400_BAD_REQUEST: self._400_response("Invalid name", "name"),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["body", "name"],
                "Input should be a valid string",
            ),
        }

        return responses

    def reset_password(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            status.HTTP_401_UNAUTHORIZED: self._401_response(),
            status.HTTP_400_BAD_REQUEST: self._400_response(
                "Invalid old password", "old_password"
            ),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["body", "old_password"],
                "Input should be a valid string",
            ),
            status.HTTP_409_CONFLICT: self._409_response(
                "The new password matches the old one",
                {"detail": "Matching passwords"},
            ),
        }

        return responses


user_profile_docs = UserProfileDocumentation()
