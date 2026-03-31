from prompt_guard_service.config import Settings


def test_tokenizer_path_defaults_to_model_directory_for_onnx_files() -> None:
    settings = Settings(
        model_path="/models/prompt-guard/model.onnx",
        tokenizer_path=None,
        lazy_load_model=True,
    )

    assert settings.resolved_model_path.as_posix() == "/models/prompt-guard/model.onnx"
    assert settings.resolved_tokenizer_path == "/models/prompt-guard"
