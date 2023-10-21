from fastapi import APIRouter


router = APIRouter(
    prefix="/profile", tags=["User profile"], responses={404: {"description": "Not found"}}
)

