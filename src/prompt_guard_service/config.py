from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PROMPT_GUARD_",
        env_file=".env",
        extra="ignore",
    )

    app_name: str = "prompt-guard-service"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"
    model_path: str = Field(default="./model/model.onnx")
    tokenizer_path: str | None = None
    lazy_load_model: bool = False

    @property
    def resolved_model_path(self) -> Path:
        return Path(self.model_path)

    @property
    def resolved_tokenizer_path(self) -> str:
        if self.tokenizer_path:
            return self.tokenizer_path
        model_path = self.resolved_model_path
        if model_path.suffix == ".onnx":
            return str(model_path.parent)
        return str(model_path)

    def model_exists(self) -> bool:
        return self.resolved_model_path.exists()
