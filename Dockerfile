FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN python -m pip install --no-cache-dir uv

COPY pyproject.toml README.md ./
COPY src ./src

RUN uv venv /app/.venv && \
    uv pip install --python /app/.venv/bin/python .

COPY .env.example ./

ENV PATH="/app/.venv/bin:${PATH}"

EXPOSE 8000

CMD ["uvicorn", "prompt_guard_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
