from fastapi import APIRouter, Depends

from app.api.dependencies.services import get_attempt_service
from app.api.dependencies.user import get_current_user_id
from app.models.schemas.attempts import AttemptQuestionAnswers
from app.services.attempt import AttemptService

router = APIRouter(prefix="/attempts", tags=["Attempts"])


@router.post("/{attempt_id}/answer-question/{question_id}/", response_model=None)
async def answer_question(
    attempt_id: int,
    question_id: int,
    answers: AttemptQuestionAnswers,
    current_user_id: int = Depends(get_current_user_id),
    attempt_service: AttemptService = Depends(get_attempt_service),
) -> None:
    """
    ### Allows to answer a specific question in quiz's attempt
    """
    return await attempt_service.answer_question(
        attempt_id, question_id, answers, current_user_id
    )
