from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PredictionItem(BaseModel):
    label: str
    score: float


class TrackHistoryItem(BaseModel):
    track_id: int
    artist: str | None
    title: str | None
    source_type: str
    original_filename: str | None
    spotify_url: str | None

    job_id: int | None
    job_status: str | None
    job_progress: int | None
    job_error_message: str | None

    transcription: str | None

    genre: str | None
    genre_confidence: float | None
    top_genres: list[PredictionItem] | None

    mood: str | None
    mood_confidence: float | None
    top_moods: list[PredictionItem] | None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)