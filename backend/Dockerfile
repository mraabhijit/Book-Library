FROM python:3.11-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.10.2 /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

ENV UV_NO_DEV=1

RUN uv sync --locked

COPY . .

CMD ["uv", "run", "fastapi", "run", "app/main.py", "--host", "0.0.0.0"]
