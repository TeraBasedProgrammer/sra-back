from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.models.db.companies import RoleEnum
from app.repository.company import CompanyRepository
from app.repository.question import QuestionRepository
from app.repository.quiz import QuizRepository
from app.services.base import BaseService
from app.utilities.formatters.http_error import error_wrapper


class QuestionService(BaseService):
    def __init__(
        self,
        quiz_repository: QuizRepository,
        question_repository: QuestionRepository,
        company_repository: CompanyRepository,
    ) -> None:
        self.quiz_repository = quiz_repository
        self.question_repository = question_repository
        self.company_repository = company_repository
