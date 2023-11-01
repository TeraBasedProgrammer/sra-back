from typing import Any

from fastapi import APIRouter

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


@router.post("/create/", status_code=201)
async def create_company() -> Any:
    pass


@router.post(
    "/",
)
async def get_user_companies() -> Any:
    pass
