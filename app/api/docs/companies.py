from fastapi import status

from app.api.docs.base import ResponseDocumentation
from app.utilities.formatters.http_error import error_wrapper


class CompanyDocumentation(ResponseDocumentation):
    def _default_company_responses(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            status.HTTP_401_UNAUTHORIZED: self._401_response(),
            status.HTTP_404_NOT_FOUND: self._404_response(),
        }
        return responses

    def get_company(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            **self._default_company_responses(),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["path", "company_id"],
                "Input should be a valid integer, unable to parse string as an integer",
            ),
        }

        return responses

    def get_tags_list(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            **self._default_company_responses(),
            status.HTTP_403_FORBIDDEN: self._403_response(),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["path", "company_id"],
                "Input should be a valid integer, unable to parse string as an integer",
            ),
        }

        return responses

    def create_company(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            status.HTTP_401_UNAUTHORIZED: self._401_response(),
            status.HTTP_400_BAD_REQUEST: self._400_response(
                "This field may contain only english letters, numbers and special characters (.-'!()/ )",
                "title",
            ),
            status.HTTP_409_CONFLICT: self._409_response(
                "Company with provided title already exists",
                {
                    "detail": error_wrapper(
                        "Company with this title already exists", "title"
                    )
                },
            ),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["body", "title"],
                "String should have at most 25 characters",
            ),
        }

        return responses

    def update_company(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            **self._default_company_responses(),
            status.HTTP_400_BAD_REQUEST: self._400_response(
                "This field may contain only english letters, numbers and special characters (.-'!()/ )",
                "title",
            ),
            status.HTTP_409_CONFLICT: self._409_response(
                "Company with provided title already exists",
                {
                    "detail": error_wrapper(
                        "Company with this title already exists", "title"
                    )
                },
            ),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["path", "company_id"],
                "Input should be a valid integer, unable to parse string as an integer",
            ),
        }

        return responses

    def get_company_member(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            **self._default_company_responses(),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["path", "company_id"],
                "Input should be a valid integer, unable to parse string as an integer",
            ),
            status.HTTP_403_FORBIDDEN: self._403_response(),
        }

        return responses

    def add_member(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            **self._default_company_responses(),
            status.HTTP_400_BAD_REQUEST: self._400_response(
                "Invalid role",
                "role",
            ),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["path", "company_id"],
                "Input should be a valid integer, unable to parse string as an integer",
            ),
            status.HTTP_403_FORBIDDEN: self._403_response(),
            status.HTTP_409_CONFLICT: self._409_response(
                "User with provided email already exists",
                {
                    "detail": error_wrapper(
                        "User with this email already exists", "email"
                    )
                },
            ),
        }

        return responses

    def update_company_member(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            **self._default_company_responses(),
            status.HTTP_400_BAD_REQUEST: self._400_response(
                "Invalid role",
                "role",
            ),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["path", "company_id"],
                "Input should be a valid integer, unable to parse string as an integer",
            ),
            status.HTTP_403_FORBIDDEN: self._403_response(),
        }

        return responses

    def delete_company_member(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            **self._default_company_responses(),
            status.HTTP_400_BAD_REQUEST: self._400_response(
                "You can't delete yourself from the company",
                "member_id",
            ),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["path", "company_id"],
                "Input should be a valid integer, unable to parse string as an integer",
            ),
            status.HTTP_403_FORBIDDEN: self._403_response(),
        }

        return responses


company_docs = CompanyDocumentation()
