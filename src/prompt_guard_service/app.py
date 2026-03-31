from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from prompt_guard_service.classifier import PromptGuardClassifier
from prompt_guard_service.config import Settings
from prompt_guard_service.schemas import HealthResponse, PredictionResult, PredictRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings: Settings = app.state.settings
    classifier: Any = app.state.classifier
    if not settings.lazy_load_model and hasattr(classifier, "load"):
        classifier.load()
    yield



def create_app(
    settings: Settings | None = None,
    classifier: PromptGuardClassifier | Any | None = None,
) -> FastAPI:
    app_settings = settings or Settings()
    app_classifier = classifier or PromptGuardClassifier(app_settings)

    app = FastAPI(title=app_settings.app_name, lifespan=lifespan)
    app.state.settings = app_settings
    app.state.classifier = app_classifier

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        loaded = bool(getattr(app.state.classifier, "loaded", False))
        return HealthResponse(
            status="ok",
            model_loaded=loaded,
            model_path=app.state.settings.model_path,
        )

    @app.post("/predict", response_model=PredictionResult)
    async def predict(payload: PredictRequest) -> PredictionResult:
        return app.state.classifier.classify(payload.text)

    return app


app = create_app()
