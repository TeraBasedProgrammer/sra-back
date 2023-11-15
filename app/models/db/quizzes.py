import enum

from sqlalchemy import (
    Boolean,
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class QuestionTypeEnum(enum.Enum):
    SingleChoice = "single_choice"
    MultipleChoice = "multiple_choice"
    OpenAnswer = "open_answer"


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    company_id = Column(ForeignKey("companies.id", ondelete="CASCADE"))
    fully_created = Column(Boolean, nullable=False, default=False)

    # Quiz completion time (in minutes)
    completion_time = Column(Integer, nullable=False)

    # Deadlines
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=False)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)

    questions = relationship("Question", back_populates="quiz", lazy="select")
    attempts = relationship("Attempt", back_populates="quiz", lazy="select")
    tags = relationship("TagQuiz", back_populates="quizzes", lazy="select")

    @property
    def questions_count(self) -> int:
        return len(self.questions)

    __table_args__ = (UniqueConstraint("title", "company_id", name="_quiz_uc"),)


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    quiz_id = Column(ForeignKey("quizzes.id", ondelete="CASCADE"))
    fully_created = Column(Boolean, nullable=False, default=False)
    type = Column(Enum(QuestionTypeEnum), nullable=False)

    quiz = relationship("Quiz", back_populates="questions", lazy="select")
    answers = relationship("Answer", back_populates="question", lazy="select")

    __table_args__ = (UniqueConstraint("title", "quiz_id", name="_question_uc"),)


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=True)
    is_correct = Column(Boolean, nullable=False, default=False)
    question_id = Column(ForeignKey("questions.id", ondelete="CASCADE"))

    question = relationship("Question", back_populates="answers", lazy="select")

    __table_args__ = (UniqueConstraint("title", "question_id", name="_answer_uc"),)
