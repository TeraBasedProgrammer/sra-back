import json
from datetime import datetime, time, timedelta

from sqlalchemy import func, select

from app.config.logs.logger import logger
from app.core.database import redis
from app.models.db.attempts import Attempt
from app.models.db.quizzes import Quiz
from app.repository.base import BaseRepository
from app.utilities.formatters.get_args import get_args


class AttemptRepository(BaseRepository):
    model = Attempt

    async def get_attempts_count(self, user_id: int, quiz_id: int) -> int:
        logger.debug(f"Received data:\n{get_args()}")

        query = select(func.count(Attempt.id)).where(
            (Attempt.user_id == user_id) & (Attempt.quiz_id == quiz_id)
        )
        result = await self.get_many(query)
        return self.unpack(result)[0]

    async def has_ongoing_attempt(
        self, user_id: int, quiz_id: int, quiz_completion_time: int
    ) -> bool:
        logger.debug(f"Received data:\n{get_args()}")

        query = select(Attempt).where(
            (Attempt.user_id == user_id)
            & (Attempt.quiz_id == quiz_id)
            & (Attempt.start_time <= datetime.utcnow())
            & (datetime.utcnow() <= Attempt.end_time)
            & (Attempt.spent_time == time(minute=quiz_completion_time))
        )

        attempt: Attempt = await self.get_instance(query)
        if attempt:
            return True

        return False

    async def create_attempt(self, user_id: int, quiz_data: Quiz) -> int:
        logger.debug(f"Received data:\n{get_args()}")

        start_time = datetime.utcnow()
        end_time = start_time + timedelta(minutes=quiz_data.completion_time)
        new_attempt = Attempt(
            quiz_id=quiz_data.id,
            user_id=user_id,
            start_time=start_time,
            end_time=end_time,
            spent_time=time(0, quiz_data.completion_time, 0),
        )

        await self.save(new_attempt)
        return new_attempt.id

    async def get_attempt_data(self, attempt_id: int) -> Attempt:
        logger.debug(f"Received data:\n{get_args()}")

        query = select(Attempt).where(Attempt.id == attempt_id)
        return await self.get_instance(query)

    async def store_answers(
        self, attempt_data, question_id, answers: list[str] | list[int]
    ) -> None:
        logger.debug(f"Received data:\n{get_args()}")

        key = f"{attempt_data.id}:{question_id}"
        await redis.set(key, json.dumps([answer for answer in answers]), ex=86400)
