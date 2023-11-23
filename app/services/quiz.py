from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.models.db.companies import RoleEnum
from app.models.db.quizzes import QuestionTypeEnum, Quiz
from app.models.db.users import Tag, TagQuiz
from app.models.schemas.quizzes import (
    QuestionCreateInput,
    QuizCreateInput,
    QuizCreateOutput,
    QuizEmployeeSchema,
    QuizFullSchema,
    QuizListSchema,
    QuizUpdate,
)
from app.repository.company import CompanyMember, CompanyRepository
from app.repository.question import QuestionRepository
from app.repository.quiz import QuizRepository
from app.repository.tag import TagRepository
from app.services.base import BaseService
from app.utilities.formatters.http_error import error_wrapper, question_error_wrapper


class QuizService(BaseService):
    def __init__(
        self, quiz_repository, company_repository, tag_repository, question_repository
    ) -> None:
        self.quiz_repository: QuizRepository = quiz_repository
        self.company_repository: CompanyRepository = company_repository
        self.tag_repository: TagRepository = tag_repository
        self.question_repository: QuestionRepository = question_repository

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

    def _validate_question_type(self, question: QuestionCreateInput) -> None:
        # Validate each question has a correct type
        try:
            QuestionTypeEnum(question.type)
        except ValueError:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=question_error_wrapper(
                    "Invalid question type", "type", question.temp_uuid
                ),
            )

    def _validate_answers_count(self, question: QuestionCreateInput) -> None:
        # Validate questions has proper amount of answers (based on type)
        if question.type != QuestionTypeEnum.OpenAnswer and len(question.answers) < 2:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=question_error_wrapper(
                    "Question should contain at least 2 answers",
                    "answers",
                    question.temp_uuid,
                ),
            )
        elif (
            question.type == QuestionTypeEnum.OpenAnswer and len(question.answers) != 1
        ):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=question_error_wrapper(
                    "Question with open answer should have 1 answer marked as 'Correct'",
                    "answers",
                    question.temp_uuid,
                ),
            )

    def _validate_duplicate_answers(self, question: QuestionCreateInput) -> None:
        # Validate that question doesn't have duplicated answers
        answers_titles = [answer.title for answer in question.answers]
        if len(answers_titles) != len(set(answers_titles)):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=question_error_wrapper(
                    "Each answer has to have a unique title",
                    "answers",
                    question.temp_uuid,
                ),
            )

    def _validate_correct_answers_count(self, question: QuestionCreateInput) -> None:
        # Validate each question has a proper amount of correct answers (based on type)
        correct_answers = [answer for answer in question.answers if answer.is_correct]
        if (
            question.type != QuestionTypeEnum.MultipleChoice
            and len(correct_answers) != 1
        ):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=question_error_wrapper(
                    "Question should have 1 correct answer",
                    "answers",
                    question.temp_uuid,
                ),
            )
        elif (
            question.type == QuestionTypeEnum.MultipleChoice
            and len(correct_answers) < 1
        ):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=question_error_wrapper(
                    "Question should have at least 1 correct answer",
                    "answers",
                    question.temp_uuid,
                ),
            )

    async def _validate_quiz_questions(
        self, questions: list[QuestionCreateInput]
    ) -> None:
        # Validate quiz has at least 2 questions
        if len(questions) < 2:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=error_wrapper(
                    "Quiz should contain at least 2 questions", "questions"
                ),
            )

        # Validate each question has a unique temp UUID
        questions_uuids = [question.temp_uuid for question in questions]
        if len(questions_uuids) != len(set(questions_uuids)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_wrapper(
                    (
                        "Question UUID should be a unique value. Ensure "
                        "you provided a unique UUID for each question"
                    ),
                    "question_temp_uuid",
                ),
            )

        # Validate quiz questions don't  have duplicates
        question_titles = [question.title for question in questions]
        if len(question_titles) != len(set(question_titles)):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=error_wrapper(
                    "Each question has to have a unique title",
                    "questions",
                ),
            )

        for question in questions:
            self._validate_question_type(question)
            self._validate_answers_count(question)
            self._validate_duplicate_answers(question)
            self._validate_correct_answers_count(question)

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
            return QuizEmployeeSchema.from_model(quiz)

        return QuizFullSchema.from_model(quiz)

    async def get_all_company_quizzes(
        self, company_id: int, current_user_id: int
    ) -> list[QuizListSchema]:
        await self._validate_instance_exists(self.company_repository, company_id)
        await self._validate_user_permissions(
            self.company_repository,
            company_id,
            current_user_id,
            (RoleEnum.Owner, RoleEnum.Admin, RoleEnum.Tester),
        )

        company_quizzes: list[
            Quiz
        ] = await self.quiz_repository.get_all_company_quizzes(company_id)
        return [
            QuizListSchema.model_validate(quiz, from_attributes=True)
            for quiz in company_quizzes
        ]

    async def get_member_quizzes(
        self, company_id: int, current_user_id: int
    ) -> list[QuizListSchema]:
        await self._validate_instance_exists(self.company_repository, company_id)
        await self._validate_user_permissions(
            self.company_repository,
            company_id,
            current_user_id,
        )

        user_tags: list[Tag] = await self.tag_repository.get_user_tags(current_user_id)

        user_quizzes: list[Quiz] = await self.quiz_repository.get_member_quizzes(
            company_id, user_tags
        )
        return [
            QuizListSchema.model_validate(quiz, from_attributes=True)
            for quiz in user_quizzes
        ]

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
        await self._validate_tag_ids(self.tag_repository, quiz_data)
        await self._validate_quiz_questions(quiz_data.questions)

        try:
            quiz_tags = quiz_data.tags
            quiz_questions = quiz_data.questions

            # Clear related instances to save only Quiz data
            quiz_data.tags = []
            quiz_data.questions = []
            new_quiz_id: int = await self.quiz_repository.create_quiz(quiz_data)
            new_quiz_tags: list[TagQuiz] = [
                TagQuiz(tag_id=tag_id, quiz_id=new_quiz_id) for tag_id in quiz_tags
            ]

            # Save quiz questions
            await self.question_repository.save_questions(new_quiz_id, quiz_questions)
            # await self.question_repository.save_many(quiz_questions)

            # Save new tag objects directly
            await self.tag_repository.save_many(new_quiz_tags)

            return QuizCreateOutput(quiz_id=new_quiz_id)
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

        if quiz_data.tags:
            await self._validate_tag_ids(self.tag_repository, quiz_data)

            # Recreate tags for the quiz
            await self.quiz_repository.delete_related_tag_quiz(quiz_id)
            await self.quiz_repository.save_many(
                [TagQuiz(tag_id=tag_id, quiz_id=quiz_id) for tag_id in quiz_data.tags]
            )
            quiz_data.tags = None

        try:
            # Validate if 'tags' field was the only field
            # (if so all fields will be None in quiz_data and an SQL exception will occur)
            if not quiz_data.are_all_attributes_none():
                await self.quiz_repository.update_quiz(quiz_id, quiz_data)
            updated_quiz: Quiz = await self.quiz_repository.get_full_quiz(quiz_id)

            return QuizFullSchema.from_model(updated_quiz)
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
