from typing import Annotated, Optional

from annotated_types import Gt
from pydantic import BaseModel, field_validator

from app.models.db.quizzes import Quiz
from app.models.schemas.tags import TagBaseSchema
from app.utilities.validators.payload.datetime import (
    validate_date_format,
    validate_time_format,
)
from app.utilities.validators.payload.text import validate_text


class AnswerSchema(BaseModel):
    title: str
    is_correct: bool
    question_id: int

    @field_validator("title")
    @classmethod
    def validate_company_title(cls, value):
        return validate_text(value, "title", min_length=5, max_length=100)


class QuestionSchema(BaseModel):
    title: str
    quiz_id: int
    type: str
    answers: list[AnswerSchema]

    @field_validator("title")
    @classmethod
    def validate_company_title(cls, value):
        return validate_text(value, "title", min_length=5, max_length=100)


class QuizBase(BaseModel):
    title: str
    description: str
    completion_time: Annotated[int, Gt(0)]
    start_date: str
    start_time: str
    end_date: str
    end_time: str

    @field_validator("title")
    @classmethod
    def validate_company_title(cls, value):
        return validate_text(value, "title", min_length=5, max_length=100)

    @field_validator("description")
    @classmethod
    def validate_description(cls, value):
        return validate_text(value, "description", min_length=25, max_length=500)

    @field_validator("start_date")
    @classmethod
    def validate_start_date(cls, value):
        return validate_date_format(value, "start_date")

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, value):
        return validate_date_format(value, "end_date")

    @field_validator("start_time")
    @classmethod
    def validate_start_time(cls, value):
        return validate_time_format(value, "start_time")

    @field_validator("end_time")
    @classmethod
    def validate_end_time(cls, value):
        return validate_time_format(value, "end_time")

    @classmethod
    def from_model(cls, quiz_instance: Quiz):
        return cls(
            title=quiz_instance.title,
            description=quiz_instance.description,
            completion_time=quiz_instance.completion_time,
            start_date=quiz_instance.start_date,
            start_time=quiz_instance.start_time,
            end_date=quiz_instance.end_date,
            end_time=quiz_instance.end_time,
        )


class QuizCreateInput(QuizBase):
    company_id: int
    tags: list[int]


class QuizCreateOutput(BaseModel):
    quiz_id: int


class QuizUpdate(QuizBase):
    title: Optional[str] = None
    description: Optional[str] = None
    completion_time: Optional[Annotated[int, Gt(0)]] = None
    start_date: Optional[str] = None
    start_time: Optional[str] = None
    end_date: Optional[str] = None
    end_time: Optional[str] = None
    tags: Optional[list[int]] = None

    def are_all_attributes_none(self) -> bool:
        # Iterate over all attributes and check if they are None
        for attr, value in self.__dict__.items():
            if value is not None:
                return False
        return True


class QuizFullSchema(QuizBase):
    company_id: int
    questions: list[QuestionSchema]
    tags: list[TagBaseSchema]

    class Config:
        from_attributes: True

    @classmethod
    def from_model(cls, quiz_instance: Quiz):
        return cls(
            **QuizBase.from_model(quiz_instance).model_dump(),
            company_id=quiz_instance.company_id,
            questions=[
                QuestionSchema(
                    title=question.questions.title,
                    quiz_id=question.questions.quiz_id,
                    type=question.questions.type,
                    answers=[
                        AnswerSchema(
                            title=answer.answers.title,
                            is_correct=answer.answers.is_correct,
                            question_id=answer.answers.question_id,
                        )
                        for answer in question.questions
                    ],
                )
                for question in quiz_instance.questions
            ],
            tags=[
                TagBaseSchema(id=tag.tags.id, title=tag.tags.title)
                for tag in quiz_instance.tags
            ],
        )


class QuizEmployeeSchema(QuizBase):
    company_id: int
    tags: list[TagBaseSchema]

    class Config:
        from_attributes: True

    @classmethod
    def from_model(cls, quiz_instance: Quiz):
        return cls(
            **QuizBase.from_model(quiz_instance).model_dump(),
            tags=[
                TagBaseSchema(id=tag.tags.id, title=tag.tags.title)
                for tag in quiz_instance.tags
            ],
        )


class QuizListSchema(BaseModel):
    id: int
    title: str
    start_time: str
    start_date: str
    end_time: str
    end_date: str
    tags: list[TagBaseSchema]
