from fastapi import APIRouter

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("/{tag_id}/")
async def get_tag(tag_id: int):
    pass


@router.post("/create/")
async def create_tag(tag_id: int):
    pass


@router.patch("/{tag_id}/update/")
async def update_tag(tag_id: int):
    pass


@router.delete("/{tag_id}/delete")
async def delete_tag(tag_id: int):
    pass
