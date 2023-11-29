from datetime import datetime, time
from typing import Any

from fastapi import HTTPException, status

from app.models.db.attempts import Attempt
from app.models.db.quizzes import Question, QuestionTypeEnum, Quiz
from app.models.schemas.attempts import AttemptQuestionAnswers
from app.models.schemas.quizzes import StartAttemptResponse
from app.repository.attempt import AttemptRepository
from app.repository.company import CompanyRepository
from app.repository.question import QuestionRepository
from app.repository.quiz import QuizRepository
from app.repository.tag import TagRepository
from app.services.base import BaseService
from app.utilities.formatters.http_error import error_wrapper


class AttemptService(BaseService):
    def __init__(
        self,
        attempt_repository: AttemptRepository,
        quiz_repository: QuizRepository,
        company_repository: CompanyRepository,
        tag_repository: TagRepository,
        question_repository: QuestionRepository,
    ) -> None:
        self.attempt_repository = attempt_repository
        self.quiz_repository = quiz_repository
        self.company_repository = company_repository
        self.tag_repository = tag_repository
        self.question_repository = question_repository

    async def _can_pass_quiz(self, user_id: int, quiz_id: int) -> bool:
        user_tags_ids: list[int] = [
            tag.id for tag in await self.tag_repository.get_user_tags(user_id)
        ]
        quiz_tags_ids: list[int] = [
            tag.id for tag in await self.tag_repository.get_quiz_tags(quiz_id)
        ]

        for tag_id in user_tags_ids:
            if tag_id in quiz_tags_ids:
                return True
        else:
            return False

    async def _has_attempts(
        self, user_id: int, quiz_id: int, max_attempts_count: int
    ) -> bool:
        user_attemps_count: int = await self.attempt_repository.get_attempts_count(
            user_id, quiz_id
        )
        if user_attemps_count == max_attempts_count:
            return False
        return True

    async def _validate_attempt_user(self, attempt_data: Attempt, user_id: int) -> None:
        if attempt_data.user_id != user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Forbidden")

    async def _validate_attempt_is_ongoing(self, attempt_data: Attempt) -> None:
        quiz_data = await self.quiz_repository.get_quiz_data(attempt_data.quiz_id)
        if not (
            attempt_data.start_time <= datetime.utcnow() <= attempt_data.end_time
            and attempt_data.spent_time == time(minute=quiz_data.completion_time)
        ):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, detail="The attempt is already over"
            )

    async def _validate_quiz_has_question(
        self, attempt_data: Attempt, question_id: int
    ) -> None:
        has_question: bool = await self.quiz_repository.has_question(
            attempt_data.quiz_id, question_id
        )
        if not has_question:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=f"Question with id '{question_id}' is not found inside the quiz",
            )

    async def _validate_answers_exist(self, question: Question, answers: list[int]):
        answers_ids = [answer.id for answer in question.answers]
        if not set(answers).issubset(answers_ids):
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=error_wrapper("Incorrect answers ids were provided", "answers"),
            )

    async def _validate_open_answer(self, answers: list[Any]) -> None:
        if len(answers) != 1 or not isinstance(answers[0], str):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=error_wrapper(
                    "You must provide a list with a single string as the answer to an 'open_answer' question",
                    "answers",
                ),
            )

    async def _validate_single_choice_answer(
        self, question: Question, answers: list[Any]
    ) -> None:
        if len(answers) != 1 or not isinstance(answers[0], int):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=error_wrapper(
                    "You must provide a list with a single integer as the answer to an 'single_choice' question",
                    "answers",
                ),
            )

        await self._validate_answers_exist(question, answers)

    async def _validate_multiple_choice_answers(
        self, question: Question, answers: list[Any]
    ) -> None:
        if not all(isinstance(elem, int) for elem in answers):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=error_wrapper(
                    "You must provide a list with answers' ids as the answer to a 'multiple_choice' question",
                    "answers",
                ),
            )

        await self._validate_answers_exist(question, answers)

    async def _validate_answers(
        self, question_id: int, answers: list[int] | list[str]
    ) -> None:
        if len(answers) < 1:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=error_wrapper("You should provide at least 1 answer", "answers"),
            )
        question: Question = await self.question_repository.get_question_by_id(
            question_id
        )

        # Validate answers based on question type
        if question.type == QuestionTypeEnum.OpenAnswer:
            await self._validate_open_answer(answers)
        if question.type == QuestionTypeEnum.SingleChoice:
            await self._validate_single_choice_answer(question, answers)
        if question.type == QuestionTypeEnum.MultipleChoice:
            await self._validate_multiple_choice_answers(question, answers)

    async def start_attempt(
        self, quiz_id: int, current_user_id: int
    ) -> StartAttemptResponse:
        await self._validate_instance_exists(self.quiz_repository, quiz_id)
        quiz: Quiz = await self.quiz_repository.get_full_quiz(quiz_id)
        await self._validate_user_permissions(
            self.company_repository, quiz.company_id, current_user_id
        )

        # Validate (by tags) that user can pass the quiz
        if not await self._can_pass_quiz(current_user_id, quiz_id):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=error_wrapper("You can't pass this quiz", "quiz_id"),
            )

        # Validate user has available attempts
        if not await self._has_attempts(
            current_user_id, quiz.id, quiz.max_attempts_count
        ):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=error_wrapper(
                    "You've used all your attempts on this quiz", "quiz_id"
                ),
            )

        # Validate that user doesn't have an ongoing attempt
        if await self.attempt_repository.has_ongoing_attempt(
            current_user_id, quiz_id, quiz.completion_time
        ):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=error_wrapper(
                    "You should finish your previous attempt to start a new one",
                    "quiz_id",
                ),
            )

        # Create a new attempt
        attempt_id = await self.attempt_repository.create_attempt(current_user_id, quiz)
        return StartAttemptResponse.from_model(attempt_id, quiz)

    async def answer_question(
        self,
        attempt_id: int,
        question_id: int,
        answers: AttemptQuestionAnswers,
        current_user_id: int,
    ) -> None:
        await self._validate_instance_exists(self.attempt_repository, attempt_id)
        await self._validate_instance_exists(self.question_repository, question_id)

        attempt_data: Attempt = await self.attempt_repository.get_attempt_data(
            attempt_id
        )
        await self._validate_attempt_user(attempt_data, current_user_id)
        await self._validate_attempt_is_ongoing(attempt_data)
        await self._validate_quiz_has_question(attempt_data, question_id)
        await self._validate_answers(question_id, answers.answers)

        await self.attempt_repository.store_answers(
            attempt_data, question_id, answers.answers
        )
