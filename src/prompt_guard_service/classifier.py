from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer

from prompt_guard_service.config import Settings
from prompt_guard_service.schemas import PredictionResult


@dataclass(slots=True)
class PromptGuardClassifier:
    settings: Settings
    session: ort.InferenceSession | None = None
    tokenizer: object | None = None
    input_names: tuple[str, ...] = ()
    output_name: str | None = None

    def load(self) -> None:
        if self.session is not None and self.tokenizer is not None:
            return

        self.tokenizer = AutoTokenizer.from_pretrained(self.settings.resolved_tokenizer_path)
        self.session = ort.InferenceSession(str(self.settings.resolved_model_path))
        self.input_names = tuple(inp.name for inp in self.session.get_inputs())
        outputs = self.session.get_outputs()
        self.output_name = outputs[0].name if outputs else None

    @property
    def loaded(self) -> bool:
        return (
            self.session is not None
            and self.tokenizer is not None
            and self.output_name is not None
        )

    def classify(self, text: str) -> PredictionResult:
        self.load()
        assert self.session is not None
        assert self.tokenizer is not None
        assert self.output_name is not None

        encoded = self.tokenizer(text, return_tensors="np", truncation=True)
        ort_inputs = {
            name: np.asarray(encoded[name], dtype=np.int64)
            for name in self.input_names
            if name in encoded
        }
        outputs = self.session.run([self.output_name], ort_inputs)
        logits = np.asarray(outputs[0])[0]
        probabilities = _softmax(logits)
        labels = self._labels_for_count(len(probabilities))
        label_scores = {
            label: float(probabilities[index]) for index, label in enumerate(labels)
        }
        top_label = max(label_scores, key=label_scores.get)
        top_score = label_scores[top_label]

        return PredictionResult(
            label=top_label,
            score=top_score,
            scores=label_scores,
            model_loaded=self.loaded,
            text_length=len(text),
        )

    @staticmethod
    def _labels_for_count(count: int) -> list[str]:
        if count == 2:
            return ["safe", "unsafe"]
        return [f"class_{index}" for index in range(count)]



def _softmax(logits: np.ndarray) -> np.ndarray:
    shifted = logits - np.max(logits)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values)
