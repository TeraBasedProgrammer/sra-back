from fastapi import status

from app.api.docs.base import ResponseDocumentation
from app.utilities.formatters.http_error import error_wrapper


class QuizDocumentation(ResponseDocumentation):
    def _default_quiz_responses(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            status.HTTP_401_UNAUTHORIZED: self._401_response(),
            status.HTTP_403_FORBIDDEN: self._403_response(),
            status.HTTP_404_NOT_FOUND: self._404_response(),
        }
        return responses

    def get_quiz(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            **self._default_quiz_responses(),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["path", "quiz_id"],
                "Input should be a valid integer, unable to parse string as an integer",
            ),
        }

        return responses

    def get_company_quizzes(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            **self._default_quiz_responses(),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["path", "company_id"],
                "Input should be a valid integer, unable to parse string as an integer",
            ),
        }

        return responses

    def get_member_quizzes(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            **self._default_quiz_responses(),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["path", "member_id"],
                "Input should be a valid integer, unable to parse string as an integer",
            ),
        }

        return responses

    def create_quiz(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            **self._default_quiz_responses(),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["body", "company_id"],
                "Input should be a valid integer, unable to parse string as an integer",
            ),
            status.HTTP_400_BAD_REQUEST: self._400_response(
                "One or more tags are not found. Ensure you passed the correct values",
                "tags",
            ),
            status.HTTP_409_CONFLICT: self._409_response(
                "Quiz with this title already exists within the company",
                {
                    "detail": error_wrapper(
                        "Quiz with this title already exists within the company",
                        "title",
                    )
                },
            ),
        }

        return responses

    def update_quiz(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            **self._default_quiz_responses(),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["body", "completion_time"],
                "Input should be a valid integer, unable to parse string as an integer",
            ),
            status.HTTP_400_BAD_REQUEST: self._400_response(
                "One or more tags are not found. Ensure you passed the correct values",
                "tags",
            ),
            status.HTTP_409_CONFLICT: self._409_response(
                "Quiz with this title already exists within the company",
                {
                    "detail": error_wrapper(
                        "Quiz with this title already exists within the company",
                        "title",
                    )
                },
            ),
        }

        return responses

    def delete_quiz(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            **self._default_quiz_responses(),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["path", "quiz_id"],
                "Input should be a valid integer, unable to parse string as an integer",
            ),
        }

        return responses

    def update_question(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            **self._default_quiz_responses(),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["body", "answers", 0, "is_correct"],
                "Input should be a valid boolean, unable to interpret input",
            ),
            status.HTTP_400_BAD_REQUEST: self._400_response(
                "Invalid question type",
                "type",
            ),
            status.HTTP_409_CONFLICT: self._409_response(
                "Question with this title already exists within the quiz",
                {
                    "detail": error_wrapper(
                        "Question with this title already exists within the quiz",
                        "title",
                    )
                },
            ),
        }

        return responses

    def delete_question(self) -> dict[int, dict]:
        responses: dict[int, dict] = {
            **self._default_quiz_responses(),
            status.HTTP_422_UNPROCESSABLE_ENTITY: self._422_response(
                ["path", "question_id"],
                "Input should be a valid integer, unable to parse string as an integer",
            ),
            status.HTTP_400_BAD_REQUEST: self._400_response(
                "The quiz shoud have at least 3 questions to perform this operation",
                None,
            ),
        }

        return responses


quiz_docs = QuizDocumentation()
