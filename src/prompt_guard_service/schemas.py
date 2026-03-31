from pydantic import BaseModel, ConfigDict, Field, field_validator


class HealthResponse(BaseModel):
    status: str = "ok"
    model_loaded: bool
    model_path: str


class PredictRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    text: str = Field(..., min_length=1, description="Input text to classify")

    @field_validator("text")
    @classmethod
    def validate_text_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must not be blank")
        return value


class PredictionResult(BaseModel):
    label: str
    score: float
    scores: dict[str, float]
    model_loaded: bool = True
    text_length: int
