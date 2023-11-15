from fastapi import APIRouter, Depends

from app.api.dependencies.services import get_quiz_service
from app.api.dependencies.user import get_current_user_id
from app.models.db.users import User
from app.models.schemas.quizzes import (
    QuizCreateInput,
    QuizCreateOutput,
    QuizEmployeeSchema,
    QuizFullSchema,
)
from app.services.quiz import QuizService

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


@router.get(
    "/{quiz_id}/", response_model=QuizFullSchema | QuizEmployeeSchema, responses=None
)
async def get_quiz(
    quiz_id: int,
    current_user_id: User = Depends(get_current_user_id),
    quiz_service: QuizService = Depends(get_quiz_service),
) -> QuizFullSchema | QuizEmployeeSchema:
    """
    ### Returns a quiz data by id
    """
    return await quiz_service.get_quiz(quiz_id, current_user_id)


@router.post("/create/", response_model=QuizCreateOutput, responses=None)
async def create_quiz(
    quiz_data: QuizCreateInput,
    current_user_id: User = Depends(get_current_user_id),
    quiz_service: QuizService = Depends(get_quiz_service),
) -> QuizCreateOutput:
    """
    Allows to create a new Quiz within the company
    """
    return await quiz_service.create_quiz(quiz_data, current_user_id)
