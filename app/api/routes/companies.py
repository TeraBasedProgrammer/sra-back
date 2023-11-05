from fastapi import APIRouter, Depends

from app.api.dependencies.auth import auth_wrapper
from app.api.dependencies.services import get_company_service, get_tag_service
from app.api.dependencies.user import get_current_user, get_current_user_id
from app.api.docs.companies import (
    get_create_company_responses,
    get_get_company_responses,
)
from app.models.db.users import User
from app.models.schemas.companies import CompanyCreate, CompanyCreateSuccess
from app.models.schemas.company_user import CompanyFullSchema
from app.models.schemas.tags import TagBaseSchema
from app.services.company import CompanyService
from app.services.tag import TagService

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


@router.get(
    "/{company_id}/",
    response_model=CompanyFullSchema,
    response_model_exclude_none=True,
    responses=get_get_company_responses(),
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


# TODO 200, 400, 403, 401, 422
@router.get("/{company_id}/tags/", response_model=list[TagBaseSchema])
async def get_tags_list(
    company_id: int,
    current_user_id: int = Depends(get_current_user_id),
    tag_service: TagService = Depends(get_tag_service),
) -> list[TagBaseSchema]:
    """
    ### Returns a list with all the available tags within the company
    """
    return await tag_service.get_company_tags(current_user_id, company_id)


@router.get("/{company_id}/tags/{tag_id}/")
async def get_company_tag(
    company_id: int,
    tag_id: int,
    current_user_id: int = Depends(get_current_user_id),
    tag_service: TagService = Depends(get_tag_service),
):
    """
    ### Returns a specific tag instance
    """
    return await tag_service.get_tag_by_id(company_id, current_user_id, tag_id)


@router.post("/create/", status_code=201, responses=get_create_company_responses())
async def create_company(
    company_data: CompanyCreate,
    current_user: User = Depends(get_current_user),
    company_service: CompanyService = Depends(get_company_service),
) -> CompanyCreateSuccess:
    """
    ### Create a new company instance
    """
    return await company_service.create_company(company_data, current_user)


@router.post("/{company_id}/tags/create/")
async def create_tag(tag_id: int):
    pass


@router.patch("/{company_id}/tags/{tag_id}/update")
async def update_tag(tag_id: int):
    pass


@router.delete("/{company_id}/tags/{tag_id}/delete")
async def delete_tag(tag_id: int):
    pass
