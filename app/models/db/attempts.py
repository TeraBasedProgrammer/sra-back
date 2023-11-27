from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Time
from sqlalchemy.orm import relationship

from app.core.database import Base


class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    quiz_id = Column(ForeignKey("quizzes.id", ondelete="CASCADE"))
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"))
    quiz = relationship("Quiz", back_populates="attempts", lazy="select")
    user = relationship("User", back_populates="attempts", lazy="select")
    start_time = Column(DateTime, default=datetime.utcnow())
    end_time = Column(DateTime)
    spent_time = Column(Time)
    result = Column(Integer, default=0)

    def __repr__(self) -> str:
        return f"Attempt for quiz {self.quiz_id}"
