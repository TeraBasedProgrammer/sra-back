from fastapi import APIRouter, Depends

from app.api.dependencies.services import get_quiz_service
from app.api.dependencies.user import get_current_user_id
from app.api.docs.quizzes import quiz_docs
from app.models.db.users import User
from app.models.schemas.quizzes import (
    QuestionSchema,
    QuestionUpdate,
    QuizCreateInput,
    QuizCreateOutput,
    QuizEmployeeSchema,
    QuizFullSchema,
    QuizUpdate,
)
from app.services.quiz import QuizService

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


@router.get(
    "/{quiz_id}/",
    response_model=QuizFullSchema | QuizEmployeeSchema,
    responses=quiz_docs.get_quiz(),
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


@router.post(
    "/create/",
    response_model=QuizCreateOutput,
    responses=quiz_docs.create_quiz(),
    status_code=201,
)
async def create_quiz(
    quiz_data: QuizCreateInput,
    current_user_id: User = Depends(get_current_user_id),
    quiz_service: QuizService = Depends(get_quiz_service),
) -> QuizCreateOutput:
    """
    Allows to create a new Quiz within the company

    Allowed question types:
    1. "single_choice"
    2. "multiple_choice"
    3. "open_answer"
    """
    return await quiz_service.create_quiz(quiz_data, current_user_id)


@router.patch(
    "/{quiz_id}/update/",
    response_model=QuizFullSchema,
    responses=quiz_docs.update_quiz(),
)
async def update_quiz(
    quiz_id: int,
    quiz_data: QuizUpdate,
    current_user_id: User = Depends(get_current_user_id),
    quiz_service: QuizService = Depends(get_quiz_service),
) -> QuizFullSchema:
    """
    Allows to update a specific Quiz instance
    """
    return await quiz_service.update_quiz(quiz_id, quiz_data, current_user_id)


@router.patch(
    "/questions/{question_id}/update/", response_model=QuestionSchema, responses=None
)
async def update_question(
    question_id: int,
    question_data: QuestionUpdate,
    current_user_id: User = Depends(get_current_user_id),
    quiz_service: QuizService = Depends(get_quiz_service),
) -> QuestionSchema:
    """
    Allows to update a specific Question instance
    """
    return await quiz_service.update_question(
        question_id, question_data, current_user_id
    )


@router.delete(
    "/{quiz_id}/delete/",
    response_model=None,
    status_code=204,
    responses=quiz_docs.delete_quiz(),
)
async def delete_quiz(
    quiz_id: int,
    current_user_id: int = Depends(get_current_user_id),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    """
    ### Allows to delete a specific Quiz instance
    """
    return await quiz_service.delete_quiz(quiz_id, current_user_id)


@router.delete(
    "/questions/{question_id}/delete/",
    response_model=None,
    responses=None,
    status_code=204,
)
async def delete_question(
    question_id: int,
    current_user_id: User = Depends(get_current_user_id),
    quiz_service: QuizService = Depends(get_quiz_service),
) -> None:
    """
    Allows to delete a specific Question instance
    """
    return await quiz_service.delete_question(question_id, current_user_id)
