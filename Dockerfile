FROM python:3.10.6-alpine as requirements-stage

WORKDIR /tmp

RUN pip install poetry

COPY ["./pyproject.toml", "./poetry.lock", "/tmp/"]

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

###

FROM python:3.10.6-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1 

WORKDIR /code

COPY ["./alembic.ini", "./pyproject.toml", "/code/"]

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

COPY ./migrations /code/migrations 

COPY ./entrypoint.sh /code/

RUN chmod +x /code/entrypoint.sh

EXPOSE 8000

ENTRYPOINT [ "/code/entrypoint.sh" ]
