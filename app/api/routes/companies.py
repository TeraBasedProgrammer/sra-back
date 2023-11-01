from fastapi import APIRouter, Depends

from app.api.dependencies.services import get_company_service
from app.api.dependencies.user import get_current_user
from app.api.docs.companies import get_create_company_responses
from app.models.db.users import User
from app.models.schemas.companies import CompanyCreate, CompanyCreateSuccess
from app.services.company import CompanyService

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


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
