from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.models.db.companies import RoleEnum
from app.models.db.quizzes import Quiz
from app.models.schemas.quizzes import (
    QuizCreateInput,
    QuizCreateOutput,
    QuizEmployeeSchema,
    QuizFullSchema,
    QuizUpdate,
)
from app.repository.company import CompanyMember, CompanyRepository
from app.repository.quiz import QuizRepository
from app.services.base import BaseService
from app.utilities.formatters.http_error import error_wrapper


class QuizService(BaseService):
    def __init__(self, quiz_repository, company_repository) -> None:
        self.quiz_repository: QuizRepository = quiz_repository
        self.company_repository: CompanyRepository = company_repository

    def _validate_quiz_deadlines(
        self, quiz_data: QuizCreateInput | QuizUpdate
    ) -> tuple[datetime]:
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

        # Return the values for the update method not to duplicate them there
        return (current_date, end_date)

    def _validate_update_quiz_deadlines(
        self, quiz_data: QuizUpdate, existing_quiz: Quiz
    ) -> None:
        current_start_date = datetime.combine(
            datetime.strptime(existing_quiz.start_date, "%d-%m-%Y").date(),
            datetime.strptime(existing_quiz.start_time, "%H:%M").time(),
        )
        start_date_is_updated: bool = any((quiz_data.start_time, quiz_data.start_date))

        # If some deadline updates are not passed use the existing ones
        # to perform the correct validation
        deadlines = ["end_date", "end_time", "start_date", "start_time"]

        for deadline in deadlines:
            if not getattr(quiz_data, deadline):
                setattr(quiz_data, deadline, getattr(existing_quiz, deadline))

        # Validate deadlines' format and retrieve them in 'datetime' format
        deadlines: tuple[datetime] = self._validate_quiz_deadlines(quiz_data)

        current_time = deadlines[0]
        end_time = deadlines[1]

        if start_date_is_updated and current_start_date <= current_time <= end_time:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=error_wrapper(
                    "You can't move the start date when current time is within the deadline",
                    "start_date",
                ),
            )

    async def get_quiz(
        self, quiz_id: int, current_user_id: int
    ) -> QuizFullSchema | QuizEmployeeSchema:
        await self._validate_instance_exists(self.quiz_repository, quiz_id)
        quiz: Quiz = await self.quiz_repository.get_full_quiz(quiz_id)
        await self._validate_user_permissions(
            self.company_repository, quiz.company_id, current_user_id
        )

        current_user_data: CompanyMember = list(
            filter(
                lambda member: member.id == current_user_id,
                await self.company_repository.get_company_members(quiz.company_id),
            )
        )[0]

        # Define what data has to be returned depending on user role
        if current_user_data.role == RoleEnum.Employee:
            return QuizEmployeeSchema.model_validate(quiz, from_attributes=True)

        return QuizFullSchema.model_validate(quiz, from_attributes=True)

    async def create_quiz(
        self, quiz_data: QuizCreateInput, current_user_id: int
    ) -> QuizCreateOutput:
        await self._validate_instance_exists(
            self.company_repository, quiz_data.company_id
        )
        await self._validate_user_permissions(
            self.company_repository,
            quiz_data.company_id,
            current_user_id,
            (RoleEnum.Owner, RoleEnum.Admin, RoleEnum.Tester),
        )

        self._validate_quiz_deadlines(quiz_data)

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

    async def update_quiz(
        self, quiz_id: int, quiz_data: QuizUpdate, current_user_id: int
    ) -> QuizFullSchema:
        await self._validate_instance_exists(self.quiz_repository, quiz_id)
        self._validate_update_data(quiz_data)

        existing_quiz_data: Quiz = await self.quiz_repository.get_quiz_data(quiz_id)
        await self._validate_user_permissions(
            self.company_repository,
            existing_quiz_data.company_id,
            current_user_id,
            (RoleEnum.Owner, RoleEnum.Admin, RoleEnum.Tester),
        )

        # Validate quiz deadlines
        deadlines = ["end_date", "end_time", "start_date", "start_time"]

        # Check if deadlines are updated, else skip validation
        for deadline in deadlines:
            if getattr(quiz_data, deadline):
                self._validate_update_quiz_deadlines(quiz_data, existing_quiz_data)
                break
        try:
            await self.quiz_repository.update_quiz(quiz_id, quiz_data)
            updated_quiz: Quiz = await self.quiz_repository.get_full_quiz(quiz_id)
            return updated_quiz
        except IntegrityError:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail=error_wrapper(
                    "Quiz with this title already exists within the company", "title"
                ),
            )

    async def delete_quiz(self, quiz_id: int, current_user_id: int) -> None:
        await self._validate_instance_exists(self.quiz_repository, quiz_id)

        quiz = await self.quiz_repository.get_full_quiz(quiz_id)

        await self._validate_user_permissions(
            self.company_repository,
            quiz.company_id,
            current_user_id,
            (RoleEnum.Owner, RoleEnum.Admin, RoleEnum.Tester),
        )

        await self.quiz_repository.delete_quiz(quiz_id)
