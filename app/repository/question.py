from app.config.logs.logger import logger
from app.models.db.quizzes import Answer, Question, QuestionTypeEnum
from app.models.schemas.quizzes import QuestionCreateInput
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
