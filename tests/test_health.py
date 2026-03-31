from fastapi.testclient import TestClient

from prompt_guard_service.app import create_app
from prompt_guard_service.config import Settings


def test_health_reports_model_not_ready_when_not_loaded() -> None:
    app = create_app(Settings(model_path="./missing-model/model.onnx", lazy_load_model=True))
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "model_loaded": False,
        "model_path": "./missing-model/model.onnx",
    }
