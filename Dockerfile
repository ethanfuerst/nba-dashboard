FROM python:3.9-slim

WORKDIR /app

RUN pip install poetry

COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-ansi --no-root

COPY . .

EXPOSE 8050

CMD ["python", "app.py", "--host", "0.0.0.0"]
