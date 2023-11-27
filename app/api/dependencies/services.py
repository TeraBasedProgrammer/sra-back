from fastapi import Depends

from app.api.dependencies.repository import get_repository
from app.repository.attempt import AttemptRepository
from app.repository.company import CompanyRepository
from app.repository.question import QuestionRepository
from app.repository.quiz import QuizRepository
from app.repository.tag import TagRepository
from app.repository.user import UserRepository
from app.services.attempt import AttemptService
from app.services.company import CompanyService
from app.services.question import QuestionService
from app.services.quiz import QuizService
from app.services.tag import TagService
from app.services.user import UserService


def get_user_service(
    user_repository: UserRepository = Depends(get_repository(UserRepository)),
) -> UserService:
    service = UserService(user_repository)
    return service


def get_company_service(
    company_repository: CompanyRepository = Depends(get_repository(CompanyRepository)),
    user_repository: UserRepository = Depends(get_repository(UserRepository)),
    tag_repository: TagRepository = Depends(get_repository(TagRepository)),
) -> CompanyService:
    service = CompanyService(company_repository, user_repository, tag_repository)
    return service


def get_tag_service(
    tag_repository: TagRepository = Depends(get_repository(TagRepository)),
    company_repository: CompanyRepository = Depends(get_repository(CompanyRepository)),
) -> TagService:
    service = TagService(tag_repository, company_repository)
    return service


def get_quiz_service(
    quiz_repository: QuizRepository = Depends(get_repository(QuizRepository)),
    company_repository: CompanyRepository = Depends(get_repository(CompanyRepository)),
    tag_repository: TagRepository = Depends(get_repository(TagRepository)),
    question_repository: QuestionRepository = Depends(
        get_repository(QuestionRepository)
    ),
) -> QuizService:
    service = QuizService(
        quiz_repository, company_repository, tag_repository, question_repository
    )
    return service


def get_question_service(
    quiz_repository: QuizRepository = Depends(get_repository(QuizRepository)),
    company_repository: CompanyRepository = Depends(get_repository(CompanyRepository)),
    question_repository: QuestionRepository = Depends(
        get_repository(QuestionRepository)
    ),
) -> QuestionService:
    service = QuestionService(quiz_repository, question_repository, company_repository)
    return service


def get_attempt_service(
    quiz_repository: QuizRepository = Depends(get_repository(QuizRepository)),
    company_repository: CompanyRepository = Depends(get_repository(CompanyRepository)),
    attempt_repository: AttemptRepository = Depends(get_repository(AttemptRepository)),
    tag_repository: TagRepository = Depends(get_repository(TagRepository)),
) -> AttemptService:
    service = AttemptService(
        attempt_repository, quiz_repository, company_repository, tag_repository
    )
    return service
