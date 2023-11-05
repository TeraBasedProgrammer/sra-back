from fastapi import Depends

from app.api.dependencies.repository import get_repository
from app.repository.company import CompanyRepository
from app.repository.tag import TagRepository
from app.repository.user import UserRepository
from app.services.company import CompanyService
from app.services.tag import TagService
from app.services.user import UserService


def get_user_service(
    user_repository: UserRepository = Depends(get_repository(UserRepository)),
) -> UserService:
    service = UserService(user_repository)
    return service


def get_company_service(
    company_repository: CompanyRepository = Depends(get_repository(CompanyRepository)),
) -> CompanyService:
    service = CompanyService(company_repository)
    return service


def get_tag_service(
    tag_repository: TagRepository = Depends(get_repository(TagRepository)),
) -> CompanyService:
    service = TagService(tag_repository)
    return service
