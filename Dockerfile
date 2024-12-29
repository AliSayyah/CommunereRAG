FROM python:3.12.4-slim-bullseye AS prod

RUN apt update && apt install -y curl
RUN pip install poetry==1.8.5

# Configuring poetry
RUN poetry config virtualenvs.create false
RUN poetry config cache-dir /tmp/poetry_cache

# Copying requirements of a project
COPY pyproject.toml poetry.lock /app/src/
WORKDIR /app/src

# Installing requirements
RUN --mount=type=cache,target=/tmp/poetry_cache poetry install --only main

# Copying actual application
COPY . /app/src/
RUN --mount=type=cache,target=/tmp/poetry_cache poetry install --only main

CMD ["/usr/local/bin/python", "-m", "CommunereRAG"]

FROM prod AS dev

RUN --mount=type=cache,target=/tmp/poetry_cache poetry install
