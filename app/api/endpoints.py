from fastapi import APIRouter

from app.api.routes.attempts import router as attempt_router
from app.api.routes.auth import router as auth_router
from app.api.routes.companies import router as company_router
from app.api.routes.quizzes import router as quiz_router
from app.api.routes.user_profile import router as profile_router
from app.api.routes.users import router as user_router


router = APIRouter()

router.include_router(router=attempt_router)
router.include_router(router=auth_router)
router.include_router(router=company_router)
router.include_router(router=quiz_router)
router.include_router(router=user_router)
router.include_router(router=profile_router)
