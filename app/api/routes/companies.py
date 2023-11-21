from fastapi import APIRouter, Depends

from app.api.dependencies.auth import auth_wrapper
from app.api.dependencies.services import (
    get_company_service,
    get_quiz_service,
    get_tag_service,
)
from app.api.dependencies.user import get_current_user, get_current_user_id
from app.api.docs.companies import company_docs
from app.models.db.users import User
from app.models.schemas.auth import UserSignUpOutput
from app.models.schemas.companies import (
    CompanyCreate,
    CompanyCreateSuccess,
    CompanyUpdate,
)
from app.models.schemas.company_user import CompanyFullSchema, UserFullSchema
from app.models.schemas.quizzes import QuizListSchema
from app.models.schemas.tags import TagBaseSchema
from app.models.schemas.users import CompanyMemberInput, CompanyMemberUpdate
from app.services.company import CompanyService
from app.services.quiz import QuizService
from app.services.tag import TagService

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


@router.get(
    "/{company_id}/",
    response_model=CompanyFullSchema,
    response_model_exclude_none=True,
    responses=company_docs.get_company(),
)
async def get_company(
    company_id: int,
    company_service: CompanyService = Depends(get_company_service),
    auth=Depends(auth_wrapper),
) -> CompanyFullSchema:
    """
    ### Return a company data by id
    """
    return await company_service.get_company_by_id(company_id)


@router.get(
    "/{company_id}/tags/",
    response_model=list[TagBaseSchema],
    responses=company_docs.get_tags_list(),
)
async def get_tags_list(
    company_id: int,
    current_user_id: int = Depends(get_current_user_id),
    tag_service: TagService = Depends(get_tag_service),
) -> list[TagBaseSchema]:
    """
    ### Returns a list with all the available tags within the company
    """
    return await tag_service.get_company_tags(current_user_id, company_id)


@router.get(
    "/{company_id}/members/{member_id}/",
    response_model=UserFullSchema,
    response_model_exclude_none=True,
    responses=company_docs.get_company_member(),
)
async def get_company_member(
    company_id: int,
    member_id: int,
    current_user_id: User = Depends(get_current_user_id),
    company_service: CompanyService = Depends(get_company_service),
) -> UserFullSchema:
    """
    ### Allows company administration to retrieve a specific member
    """
    return await company_service.get_member(company_id, member_id, current_user_id)


@router.get("/{company_id}/quizzes/", response_model=list[QuizListSchema])
async def get_company_quizzes(
    company_id: int,
    current_user_id: User = Depends(get_current_user_id),
    quiz_service: QuizService = Depends(get_quiz_service),
) -> list[QuizListSchema]:
    """
    ### Returns a list with all the available quizzes within the company
    """
    return await quiz_service.get_all_company_quizzes(company_id, current_user_id)


@router.get("/{company_id}/quizzes/for-me/", response_model=list[QuizListSchema])
async def get_member_quizzes(
    company_id: int,
    current_user_id: User = Depends(get_current_user_id),
    quiz_service: QuizService = Depends(get_quiz_service),
) -> list[QuizListSchema]:
    """
    ### Returns a list with all the available quizzes for the specific company member
    """
    return await quiz_service.get_member_quizzes(company_id, current_user_id)


@router.post("/create/", status_code=201, responses=company_docs.create_company())
async def create_company(
    company_data: CompanyCreate,
    current_user: User = Depends(get_current_user),
    company_service: CompanyService = Depends(get_company_service),
) -> CompanyCreateSuccess:
    """
    ### Create a new company instance
    """
    return await company_service.create_company(company_data, current_user)


@router.post(
    "/{company_id}/members/add/",
    status_code=201,
    responses=company_docs.add_member(),
    response_model=UserSignUpOutput,
)
async def add_company_member(
    company_id: int,
    member_data: CompanyMemberInput,
    current_user_id: User = Depends(get_current_user_id),
    company_service: CompanyService = Depends(get_company_service),
) -> UserSignUpOutput:
    """
    ### Allows company administration to add new members

    Available roles:
    1. "admin"
    2. "tester"
    3. "employee"
    """
    return await company_service.add_member(company_id, member_data, current_user_id)


@router.patch(
    "/{company_id}/members/{member_id}/update/",
    response_model=UserFullSchema,
    response_model_exclude_none=True,
    responses=company_docs.update_company_member(),
)
async def update_company_member(
    company_id: int,
    member_id: int,
    member_data: CompanyMemberUpdate,
    current_user_id: User = Depends(get_current_user_id),
    company_service: CompanyService = Depends(get_company_service),
) -> UserFullSchema:
    """
    ### Allows company administration to update a specific member

    Available roles:
    1. "admin"
    2. "tester"
    3. "employee"
    """
    return await company_service.update_member(
        company_id, member_id, member_data, current_user_id
    )


@router.patch(
    "/{company_id}/update/",
    responses=company_docs.update_company(),
    response_model=CompanyFullSchema,
    response_model_exclude_none=True,
)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    current_user_id: User = Depends(get_current_user_id),
    company_service: CompanyService = Depends(get_company_service),
) -> CompanyFullSchema:
    """
    ### Update a specific company instance
    """
    return await company_service.update_company(
        company_id, company_data, current_user_id
    )


@router.delete(
    "/{company_id}/members/{member_id}/delete/",
    response_model=None,
    responses=company_docs.delete_company_member(),
    status_code=204,
)
async def delete_company_member(
    company_id: int,
    member_id: int,
    current_user_id: User = Depends(get_current_user_id),
    company_service: CompanyService = Depends(get_company_service),
):
    """
    ### Allows company administration to delete a specific member
    """
    return await company_service.delete_member(company_id, member_id, current_user_id)
