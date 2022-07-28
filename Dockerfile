FROM python:3.10 as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        build-essential \
        curl \
    && curl -sSL https://install.python-poetry.org | python3.10 -

WORKDIR /code
COPY poetry.lock pyproject.toml .dockerignore /code/

RUN /root/.local/bin/poetry install --no-interaction --no-ansi

# FIXME: Confused, seems to completly ignore the .dockerignore file
COPY . /code

# replace the database.ini file with the docker version
#COPY db/db_config/database_docker.ini /code/db/db_config/database.ini
#RUN make install_docker
