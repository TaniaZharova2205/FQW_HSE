from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PredictionItem(BaseModel):
    label: str
    score: float


class AnalysisResultRead(BaseModel):
    id: int
    track_id: int
    transcription: str | None

    genre: str | None
    genre_confidence: float | None
    top_genres: list[PredictionItem] | None

    mood: str | None
    mood_confidence: float | None
    top_moods: list[PredictionItem] | None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)