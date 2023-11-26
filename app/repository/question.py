from sqlalchemy import delete, select
from sqlalchemy.orm import joinedload

from app.config.logs.logger import logger
from app.models.db.quizzes import Answer, Question, QuestionTypeEnum
from app.models.schemas.quizzes import QuestionCreateInput, QuestionUpdate
from app.repository.base import BaseRepository
from app.utilities.formatters.get_args import get_args


class QuestionRepository(BaseRepository):
    model = Question

    async def save_questions(
        self, quiz_id: int, question_data: list[QuestionCreateInput]
    ) -> None:
        logger.debug(f"Received data:\n{get_args()}")

        questions: list[Question] = []
        for question in question_data:
            questions.append(
                Question(
                    title=question.title,
                    quiz_id=quiz_id,
                    type=QuestionTypeEnum(question.type),
                    answers=[
                        Answer(title=answer.title, is_correct=answer.is_correct)
                        for answer in question.answers
                    ],
                )
            )

        await self.save_many(questions)

        logger.debug(
            f"Successfully inserted saved questions of the quiz instance '{quiz_id}'"
        )

    async def delete_question_answers(self, question_id: int) -> None:
        logger.debug(f"Received data:\n{get_args()}")
        await self.async_session.execute(
            delete(Answer).where(Answer.question_id == question_id)
        )
        logger.debug(f'Successfully deleted question "{question_id}" answers')

    async def update_question(
        self, quiz_id: int, question_id: int, question_data: QuestionUpdate
    ) -> None:
        logger.debug(f"Received data:\n{get_args()}")

        # Update answers separately if they're provided
        if question_data.answers:
            await self.delete_question_answers(question_id)
            answers = [
                Answer(
                    question_id=question_id,
                    title=answer.title,
                    is_correct=answer.is_correct,
                )
                for answer in question_data.answers
            ]
            await self.save_many(answers)
            question_data.answers = None

        await self.update(question_id, question_data)
        logger.debug(f'Successfully updatetd question instance "{question_id}"')

    async def get_question_by_id(self, question_id: int) -> Question:
        logger.debug(f"Received data:\n{get_args()}")

        query = (
            select(Question)
            .options(joinedload(Question.answers))
            .where(Question.id == question_id)
        )

        result: Question = await self.get_instance(query)
        if result:
            logger.debug(f'Retrieved question by id "{question_id}": "{result}"')

        return result

    async def delete_question(self, question_id: int) -> None:
        logger.debug(f"Received data:\n{get_args()}")
        result = await self.delete(question_id)

        logger.debug(
            f'Successfully deleted question instance "{question_id}" from the database'
        )
        return result
