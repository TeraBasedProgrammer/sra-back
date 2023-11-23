from sqlalchemy import delete, select
from sqlalchemy.orm import joinedload

from app.config.logs.logger import logger
from app.models.db.quizzes import Question, Quiz
from app.repository.base import BaseRepository
from app.utilities.formatters.get_args import get_args


class QuestionRepository(BaseRepository):
    model = Question

    async def create_question(self, question_data) -> Question:
        pass
