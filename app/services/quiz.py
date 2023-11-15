from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.models.db.companies import RoleEnum
from app.models.db.quizzes import Quiz
from app.models.schemas.quizzes import QuizCreateInput, QuizCreateOutput, QuizUpdate
from app.repository.company import CompanyRepository
from app.repository.quiz import QuizRepository
from app.services.base import BaseService
from app.utilities.formatters.http_error import error_wrapper


class QuizService(BaseService):
    def __init__(self, quiz_repository, company_repository) -> None:
        self.quiz_repository: QuizRepository = quiz_repository
        self.company_repository: CompanyRepository = company_repository

    async def _validate_quiz_deadlines(
        self, quiz_data: QuizCreateInput | QuizUpdate
    ) -> None:
        current_date = datetime.utcnow()

        # Set seconds and microseconds to get rid of unnecessary precision
        current_date = current_date.replace(second=0, microsecond=0)

        start_date = datetime.combine(
            datetime.strptime(quiz_data.start_date, "%d-%m-%Y").date(),
            datetime.strptime(quiz_data.start_time, "%H:%M").time(),
        )
        end_date = datetime.combine(
            datetime.strptime(quiz_data.end_date, "%d-%m-%Y").date(),
            datetime.strptime(quiz_data.end_time, "%H:%M").time(),
        )

        if start_date <= current_date:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=error_wrapper(
                    "Quiz start date can't be in the past or right now", "start_date"
                ),
            )
        elif end_date <= current_date:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=error_wrapper(
                    "Quiz end date can't be in the past or right now", "end_date"
                ),
            )
        elif end_date <= start_date:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=error_wrapper(
                    "The end date can't be earlier than the start date or be the same",
                    "end_date",
                ),
            )

    async def create_quiz(
        self, quiz_data: QuizCreateInput, current_user_id: int
    ) -> QuizCreateOutput:
        await self._validate_instance_exists(
            self.company_repository, quiz_data.company_id
        )
        await self._validate_user_membership(
            self.company_repository,
            quiz_data.company_id,
            current_user_id,
            (RoleEnum.Owner, RoleEnum.Admin, RoleEnum.Tester),
        )

        await self._validate_quiz_deadlines(quiz_data)

        try:
            quiz: Quiz = await self.quiz_repository.create_quiz(quiz_data)
            return QuizCreateOutput(quiz_id=quiz.id)
        except IntegrityError:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail=error_wrapper(
                    "Quiz with this title already exists within the company", "title"
                ),
            )
