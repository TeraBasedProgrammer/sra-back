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
