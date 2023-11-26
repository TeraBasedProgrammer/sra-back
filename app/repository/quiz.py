from sqlalchemy import delete, func, select
from sqlalchemy.orm import joinedload

from app.config.logs.logger import logger
from app.models.db.quizzes import Question, Quiz
from app.models.db.users import Tag, TagQuiz
from app.models.schemas.quizzes import QuizCreateInput, QuizUpdate
from app.repository.base import BaseRepository
from app.utilities.formatters.get_args import get_args


class QuizRepository(BaseRepository):
    model = Quiz

    async def create_quiz(self, quiz_data: QuizCreateInput) -> int:
        logger.debug(f"Received data:\n{get_args()}")

        new_quiz: Quiz = await self.create(quiz_data)

        logger.debug("Successfully inserted new quiz instance into the database")
        return new_quiz.id

    async def get_full_quiz(self, quiz_id: int) -> Quiz:
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

    async def get_quiz_data(self, quiz_id: int) -> Quiz:
        logger.debug(f"Received data:\n{get_args()}")

        query = select(Quiz).where(Quiz.id == quiz_id)

        result: Quiz = await self.get_instance(query)
        if result:
            logger.debug(f'Retrieved quiz data by id "{quiz_id}": "{result}"')
        return result

    async def get_all_company_quizzes(self, company_id: int) -> list[Quiz]:
        logger.debug(f"Received data:\n{get_args()}")

        query = (
            select(Quiz)
            .options(joinedload(Quiz.tags))
            .where(Quiz.company_id == company_id)
        )

        result: list[Quiz] = self.unpack(await self.get_many(query))
        if result:
            logger.debug(f'Retrieved quiz list by company id : "{result}"')

            # Temporaty solution to make m2m fields compatible with Pydantic
            for quiz in result:
                quiz.tags = [tag.tags for tag in quiz.tags]
        return result

    async def get_member_quizzes(
        self, company_id: int, user_tags: list[Tag]
    ) -> list[Quiz]:
        logger.debug(f"Received data:\n{get_args()}")
        tag_ids = [tag.id for tag in user_tags]

        query = (
            select(Quiz)
            .join(TagQuiz, TagQuiz.quiz_id == Quiz.id)
            .where((Quiz.company_id == company_id) & (TagQuiz.tag_id.in_(tag_ids)))
        )

        result: list[Quiz] = self.unpack(await self.get_many(query))
        if result:
            logger.debug(f'Retrieved quiz list by company id : "{result}"')

            # Temporaty solution to make m2m fields compatible with Pydantic
            for quiz in result:
                quiz.tags = [tag.tags for tag in quiz.tags]
        return result

    async def get_quiz_company_id(self, quiz_id: int) -> int:
        logger.debug(f"Received data:\n{get_args()}")

        query = (select(Quiz).where(Quiz.id == quiz_id)).with_only_columns(
            Quiz.company_id
        )

        result = await self.async_session.execute(query)
        logger.debug(f'Retrieved quiz "{quiz_id}" company_id: "{result}"')
        return result.scalar_one_or_none()

    async def get_questions_count(self, quiz_id: int) -> int:
        logger.debug(f"Received data:\n{get_args()}")

        result = await self.async_session.execute(
            select(func.count(Question.id)).where(Question.quiz_id == quiz_id)
        )
        return result.scalar_one_or_none()

    async def update_quiz(self, quiz_id: int, quiz_data: QuizUpdate) -> Quiz:
        logger.debug(f"Received data:\n{get_args()}")
        updated_quiz = await self.update(quiz_id, quiz_data)

        logger.debug(f'Successfully updatetd quiz instance "{quiz_id}"')
        return updated_quiz

    async def delete_quiz(self, quiz_id) -> None:
        logger.debug(f"Received data:\n{get_args()}")
        result = await self.delete(quiz_id)

        logger.debug(
            f'Successfully deleted quiz instance "{quiz_id}" from the database'
        )
        return result

    async def delete_related_tag_quiz(self, quiz_id: int) -> None:
        logger.debug(f"Received data:\n{get_args()}")

        # Delete all relataed TagQuiz objects
        await self.async_session.execute(
            delete(TagQuiz).where(TagQuiz.quiz_id == quiz_id)
        )
        await self.async_session.commit()
