from fastapi import status

from app.api.docs.base import ResponseDocumentation


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
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["body", "title"],
                "String should have at most 25 characters",
            ),
        }

        return responses


company_docs = CompanyDocumentation()
