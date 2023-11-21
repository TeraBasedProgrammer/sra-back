from fastapi import status

from app.api.docs.base import ResponseDocumentation
from app.utilities.formatters.http_error import error_wrapper


class TagDocumentantion(ResponseDocumentation):
    def _default_tag_responses(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            status.HTTP_401_UNAUTHORIZED: self._401_response(),
            status.HTTP_403_FORBIDDEN: self._403_response(),
            status.HTTP_404_NOT_FOUND: self._404_response(),
        }
        return responses

    def get_tag(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            **self._default_tag_responses(),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["path", "tag_id"],
                "Input should be a valid integer, unable to parse string as an integer",
            ),
        }

        return responses

    def create_tag(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            **self._default_tag_responses(),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["body", "title"],
                "Input should be a valid string",
            ),
            status.HTTP_409_CONFLICT: self._409_response(
                "Tag with the provided title already exists within the company",
                {
                    "detail": error_wrapper(
                        "The company already has a tag with provided title", "title"
                    )
                },
            ),
        }

        return responses

    def update_tag(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            **self._default_tag_responses(),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["body", "title"],
                "Input should be a valid string",
            ),
            status.HTTP_400_BAD_REQUEST: self._400_response(
                "At least one valid field should be provided", None
            ),
            status.HTTP_409_CONFLICT: self._409_response(
                "Tag with the provided title already exists within the company",
                {
                    "detail": error_wrapper(
                        "The company already has a tag with provided title", "title"
                    )
                },
            ),
        }

        return responses

    def delete_tag(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            **self._default_tag_responses(),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["path", "tag_id"],
                "Input should be a valid integer, unable to parse string as an integer",
            ),
            status.HTTP_400_BAD_REQUEST: self._400_response(
                "At least one valid field should be provided", None
            ),
        }

        return responses


tag_docs = TagDocumentantion()
