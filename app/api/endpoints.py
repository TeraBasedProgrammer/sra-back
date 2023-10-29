from fastapi import APIRouter

from app.api.routes.attempts import router as attempt_router
from app.api.routes.auth import router as auth_router
from app.api.routes.companies import router as company_router
from app.api.routes.quizzes import router as quiz_router
from app.api.routes.user_profile import router as profile_router
from app.api.routes.users import router as user_router

responses = {
    401: {
        "description": "Authentication error",
        "content": {"application/json": {"example": {"detail": "Not authenticated"}}},
    },
    400: {
        "description": "Validation error",
        "content": {"application/json": {"example": {"detail": "Validation error"}}},
    },
    403: {
        "description": "Permission error",
        "content": {"application/json": {"example": {"detail": "Forbidden"}}},
    },
    422: {
        "description": "Unprocessable entity",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {"loc": ["string", 0], "msg": "string", "type": "string"}
                    ]
                }
            }
        },
    },
    404: {
        "description": "Instance is not found",
        "content": {
            "application/json": {"example": {"detail": "Instance is not found"}}
        },
    },
}

router = APIRouter()

router.include_router(router=attempt_router)
router.include_router(
    router=auth_router,
    responses={422: responses[422], 400: responses[400]},
)
router.include_router(router=company_router)
router.include_router(router=quiz_router)
router.include_router(router=user_router)
router.include_router(router=profile_router)
