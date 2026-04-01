FROM python:3.13-slim

ARG MODEL_BASE_URL=https://huggingface.co/gravitee-io/Llama-Prompt-Guard-2-86M-onnx/resolve/main
ARG MODEL_FILE_NAME=model.quant.onnx

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    MODEL_BASE_URL=${MODEL_BASE_URL} \
    MODEL_FILE_NAME=${MODEL_FILE_NAME}

WORKDIR /app

RUN python -m pip install --no-cache-dir uv

COPY pyproject.toml README.md ./
COPY src ./src

RUN uv venv /app/.venv && \
    uv pip install --python /app/.venv/bin/python .

COPY .env.example ./

RUN mkdir -p /app/model && python - <<'PY'
import os
import urllib.request
from pathlib import Path

base_url = os.environ["MODEL_BASE_URL"].rstrip("/")
model_file_name = os.environ["MODEL_FILE_NAME"]
files = [
    model_file_name,
    "config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "special_tokens_map.json",
]
target_dir = Path("/app/model")
for file_name in files:
    urllib.request.urlretrieve(f"{base_url}/{file_name}", target_dir / file_name)
PY

ENV PATH="/app/.venv/bin:${PATH}"

EXPOSE 8000

CMD ["uvicorn", "prompt_guard_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
