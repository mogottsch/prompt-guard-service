from fastapi.testclient import TestClient

from prompt_guard_service.app import create_app
from prompt_guard_service.config import Settings
from prompt_guard_service.schemas import PredictionResult


class StubClassifier:
    def classify(self, text: str) -> PredictionResult:
        return PredictionResult(
            label="safe",
            score=0.91,
            scores={"safe": 0.91, "unsafe": 0.09},
            model_loaded=True,
            text_length=len(text),
        )



def test_predict_returns_classification_payload() -> None:
    app = create_app(Settings(lazy_load_model=True), classifier=StubClassifier())
    client = TestClient(app)

    response = client.post("/predict", json={"text": "hello world"})

    assert response.status_code == 200
    assert response.json() == {
        "label": "safe",
        "score": 0.91,
        "scores": {"safe": 0.91, "unsafe": 0.09},
        "model_loaded": True,
        "text_length": 11,
    }



def test_predict_rejects_blank_text() -> None:
    app = create_app(Settings(lazy_load_model=True), classifier=StubClassifier())
    client = TestClient(app)

    response = client.post("/predict", json={"text": "   "})

    assert response.status_code == 422
