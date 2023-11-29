from pydantic import BaseModel


class AttemptQuestionAnswers(BaseModel):
    answers: list[int] | list[str]
