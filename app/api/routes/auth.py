from fastapi import APIRouter


router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/something")
async def get_hyina() -> None:
    return {"something": 123}