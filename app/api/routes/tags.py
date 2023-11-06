from fastapi import APIRouter, Depends

from app.api.dependencies.services import get_tag_service
from app.api.dependencies.user import get_current_user_id
from app.services.tag import TagService

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("/{tag_id}/")
async def get_tag(
    tag_id: int,
    current_user_id: int = Depends(get_current_user_id),
    tag_service: TagService = Depends(get_tag_service),
):
    """
    ### Returns a specific tag instance
    """
    return await tag_service.get_tag_by_id(current_user_id, tag_id)


@router.post("/create/")
async def create_tag(tag_id: int):
    pass


@router.patch("/{tag_id}/update/")
async def update_tag(tag_id: int):
    pass


@router.delete("/{tag_id}/delete/")
async def delete_tag(tag_id: int):
    pass
