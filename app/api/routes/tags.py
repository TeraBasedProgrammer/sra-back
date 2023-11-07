from fastapi import APIRouter, Depends

from app.api.dependencies.services import get_tag_service
from app.api.dependencies.user import get_current_user_id
from app.models.schemas.tags import (
    TagCreateInput,
    TagCreateOutput,
    TagSchema,
    TagUpdateInput,
)
from app.services.tag import TagService

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("/{tag_id}/", response_model=TagSchema)
async def get_tag(
    tag_id: int,
    current_user_id: int = Depends(get_current_user_id),
    tag_service: TagService = Depends(get_tag_service),
) -> TagSchema:
    """
    ### Returns a specific tag instance
    """
    return await tag_service.get_tag_by_id(current_user_id, tag_id)


@router.post("/create/", response_model=TagCreateOutput)
async def create_tag(
    tag_data: TagCreateInput,
    current_user_id: int = Depends(get_current_user_id),
    tag_service: TagService = Depends(get_tag_service),
) -> TagCreateOutput:
    """
    ### Allows to create a new Tag instance within a company
    """
    return await tag_service.create_tag(tag_data, current_user_id)


@router.patch("/{tag_id}/update/", response_model=TagSchema)
async def update_tag(
    tag_id: int,
    tag_data: TagUpdateInput,
    current_user_id: int = Depends(get_current_user_id),
    tag_service: TagService = Depends(get_tag_service),
) -> TagSchema:
    """
    ### Allows to update a specific Tag instance
    """
    return await tag_service.update_tag(tag_id, tag_data, current_user_id)


@router.delete("/{tag_id}/delete/", response_model=None, status_code=204)
async def delete_tag(
    tag_id: int,
    current_user_id: int = Depends(get_current_user_id),
    tag_service: TagService = Depends(get_tag_service),
):
    """
    ### Allows to delete a specific Tag instance
    """
    return await tag_service.delete_tag(tag_id, current_user_id)
