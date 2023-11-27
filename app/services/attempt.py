from fastapi import HTTPException, status

from app.models.db.quizzes import Quiz
from app.models.schemas.quizzes import StartAttemptResponse
from app.repository.attempt import AttemptRepository
from app.repository.company import CompanyRepository
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
    ) -> None:
        self.attempt_repository = attempt_repository
        self.quiz_repository = quiz_repository
        self.company_repository = company_repository
        self.tag_repository = tag_repository

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
                    "You've user all your attempts on this quiz", "quiz_id"
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
