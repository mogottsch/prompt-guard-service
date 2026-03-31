from fastapi.testclient import TestClient

from prompt_guard_service.app import create_app
from prompt_guard_service.config import Settings


class StubClassifier:
    def __init__(self) -> None:
        self.loaded = False
        self.load_calls = 0

    def load(self) -> None:
        self.load_calls += 1
        self.loaded = True



def test_app_startup_preloads_model_when_lazy_loading_is_disabled() -> None:
    classifier = StubClassifier()
    app = create_app(Settings(lazy_load_model=False), classifier=classifier)

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert classifier.load_calls == 1
    assert classifier.loaded is True
