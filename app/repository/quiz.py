from sqlalchemy import select 
from sqlalchemy.orm import joinedload

from app.config.logs.logger import logger
from app.models.db.quizzes import Quiz
from app.models.schemas.quizzes import QuizCreateInput
from app.repository.base import BaseRepository
from app.utilities.formatters.get_args import get_args


class QuizRepository(BaseRepository):
    model = Quiz

    async def create_quiz(self, quiz_data: QuizCreateInput) -> Quiz:
        logger.debug(f"Received data:\n{get_args()}")

        new_quiz: Quiz = await self.create(quiz_data)

        logger.debug("Successfully inserted new quiz instance into the database")
        return new_quiz
    
    async def get_quiz_by_id(self, quiz_id: int) -> Quiz:
        logger.debug(f"Received data:\n{get_args()}")

        query = (
            select(Quiz)
            .options(joinedload(Quiz.questions), joinedload(Quiz.tags))
            .where(Quiz.id == quiz_id)
        )
        result: Quiz = await self.get_instance(query)
        if result:
            logger.debug(f'Retrieved quiz by id "{quiz_id}": "{result}"')
        return result
