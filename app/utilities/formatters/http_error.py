from uuid import UUID


def error_wrapper(message: str, field: str) -> dict[str, str]:
    return {"message": message, "field": field}


def question_error_wrapper(message: str, field: str, question_uuid: UUID):
    return {"message": message, "field": field, "question_uuid": question_uuid}
