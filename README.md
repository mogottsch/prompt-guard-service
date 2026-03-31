# prompt-guard-service

[![CI](https://github.com/mogottsch/prompt-guard-service/actions/workflows/ci.yml/badge.svg)](https://github.com/mogottsch/prompt-guard-service/actions/workflows/ci.yml)
[![Release](https://github.com/mogottsch/prompt-guard-service/actions/workflows/release.yml/badge.svg)](https://github.com/mogottsch/prompt-guard-service/actions/workflows/release.yml)
[![GHCR](https://img.shields.io/badge/GHCR-ghcr.io%2Fmogottsch%2Fprompt--guard--service-blue)](https://github.com/mogottsch/prompt-guard-service/pkgs/container/prompt-guard-service)

A small FastAPI service for Prompt Guard inference using ONNX Runtime.

## Stack

- Python 3.13
- `uv` for dependency and virtualenv management
- FastAPI + Pydantic v2
- ONNX Runtime
- Hugging Face tokenizer loading

## API

### `GET /health`
Returns basic liveness plus model load state.

Example response:

```json
{
  "status": "ok",
  "model_loaded": false,
  "model_path": "./model"
}
```

### `POST /predict`
Classifies a text payload.

Request:

```json
{
  "text": "hello world"
}
```

Response:

```json
{
  "label": "safe",
  "score": 0.91,
  "scores": {
    "safe": 0.91,
    "unsafe": 0.09
  },
  "model_loaded": true,
  "text_length": 11
}
```

## Config

Environment variables use the `PROMPT_GUARD_` prefix.

- `PROMPT_GUARD_MODEL_PATH` — path to ONNX model file, default `./model/model.onnx`
- `PROMPT_GUARD_TOKENIZER_PATH` — optional tokenizer path, defaults to the parent directory of `MODEL_PATH`
- `PROMPT_GUARD_LAZY_LOAD_MODEL` — set to `true` to defer model loading until first request
- `PROMPT_GUARD_HOST` — default `0.0.0.0`
- `PROMPT_GUARD_PORT` — default `8000`
- `PROMPT_GUARD_LOG_LEVEL` — default `info`

## Local development

This repo expects `uv`.

```bash
uv venv
uv sync --dev
source .venv/bin/activate
uv run uvicorn prompt_guard_service.main:app --host 0.0.0.0 --port 8000 --reload
```

If `uv` is not installed on the machine yet, install it first using your preferred method.

## Tests

```bash
uv run pytest
```

## Docker

Build locally:

```bash
docker build -t prompt-guard-service:dev .
```

Run local image:

```bash
docker run --rm -p 8000:8000 \
  -e PROMPT_GUARD_MODEL_PATH=/app/model/model.onnx \
  -v $(pwd)/model:/app/model \
  prompt-guard-service:dev
```

## Pull and run the published image

Pull latest:

```bash
docker pull ghcr.io/mogottsch/prompt-guard-service:latest
```

Pull a pinned release tag:

```bash
docker pull ghcr.io/mogottsch/prompt-guard-service:v0.1.0
```

Run the published image:

```bash
docker run --rm -p 8000:8000 \
  -e PROMPT_GUARD_MODEL_PATH=/app/model/model.onnx \
  -v $(pwd)/model:/app/model:ro \
  ghcr.io/mogottsch/prompt-guard-service:latest
```

Smoke test it:

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict \
  -H 'content-type: application/json' \
  -d '{"text":"hello world"}'
```

## CI and image publishing

GitHub Actions workflow: `.github/workflows/ci.yml`

What it does:
- runs pytest
- runs ruff
- builds a multi-arch image for `linux/amd64` and `linux/arm64`
- pushes to `ghcr.io/mogottsch/prompt-guard-service`
- adds OCI labels including the source repository
- emits build provenance attestation
- creates GitHub releases for version tags via `.github/workflows/release.yml`

Expected image names:
- `ghcr.io/mogottsch/prompt-guard-service:latest`
- `ghcr.io/mogottsch/prompt-guard-service:main`
- `ghcr.io/mogottsch/prompt-guard-service:sha-<commit>`
- `ghcr.io/mogottsch/prompt-guard-service:v0.1.0`
- semver tags on `v*` git tags

Important GHCR note:
- GitHub still creates new container packages as private by default on first publish.
- The workflow is fully ready to publish, but the first package visibility change to `public` may still need one manual GitHub UI step unless GitHub finally fixes that cringe limitation.
- After that, image pulls can be public and anonymous.

## Notes

- The service currently assumes binary classification maps to `safe` and `unsafe`.
- If the exported model uses different label semantics, update the label mapping logic.
- For Kubernetes, this repo should produce the container image, while deployment manifests stay in `kubernetes-homeserver`.
