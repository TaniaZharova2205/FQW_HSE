from pathlib import Path

import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from app.core.config import settings


class MoodService:
    _instance = None
    _tokenizer = None
    _model = None
    _device = None
    _id_to_mood = None

    MOOD_MAPPING = {
        "happy": ["joy", "amusement"],
        "romantic": ["love", "admiration"],
        "energetic": ["excitement", "optimism"],
        "calm": ["approval", "relief"],
        "sad": ["sadness", "grief", "disappointment"],
        "angry": ["anger", "annoyance", "disapproval"],
        "dark": ["disgust", "fear"],
        "nostalgic": ["nostalgia"],
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MoodService, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._model is not None and self._tokenizer is not None:
            return

        model_path = Path(settings.MOOD_MODEL_PATH)
        if not model_path.exists():
            raise FileNotFoundError(f"Mood model path not found: {model_path}")

        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self._tokenizer = AutoTokenizer.from_pretrained(
            str(model_path),
            local_files_only=True,
        )
        self._model = AutoModelForSequenceClassification.from_pretrained(
            str(model_path),
            local_files_only=True,
        )

        self._model.to(self._device)
        self._model.eval()

        mood_to_id = {mood: i for i, mood in enumerate(self.MOOD_MAPPING.keys())}
        self._id_to_mood = {v: k for k, v in mood_to_id.items()}

    @property
    def tokenizer(self):
        return self._tokenizer

    @property
    def model(self):
        return self._model

    @property
    def device(self):
        return self._device

    @property
    def id_to_mood(self):
        return self._id_to_mood

    def predict_top3(self, text: str) -> list[dict]:
        if not text or not text.strip():
            raise ValueError("Text for mood prediction is empty")

        inputs = self.tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=256,
            return_tensors="pt",
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

        probs = torch.softmax(outputs.logits, dim=-1).cpu().numpy()[0]

        top_ids = np.argsort(probs)[::-1][:3]

        return [
            {
                "label": self.id_to_mood[int(idx)],
                "score": float(probs[int(idx)]),
            }
            for idx in top_ids
        ]

    def predict_top1(self, text: str) -> dict:
        top3 = self.predict_top3(text)
        return top3[0]