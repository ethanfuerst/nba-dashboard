FROM python:3.9-slim

WORKDIR /app

RUN pip install uv

COPY uv.lock pyproject.toml ./

RUN uv config virtualenvs.create false

RUN uv sync --no-interaction --no-ansi --no-root

COPY . .

EXPOSE 8050

CMD ["python", "app.py", "--host", "0.0.0.0"]
