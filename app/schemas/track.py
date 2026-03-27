from datetime import datetime
from pydantic import BaseModel, ConfigDict, HttpUrl


class SpotifyTrackCreate(BaseModel):
    spotify_url: HttpUrl


class TrackRead(BaseModel):
    id: int
    user_id: int
    source_type: str
    spotify_url: str | None
    original_filename: str | None
    artist: str | None
    title: str | None
    audio_path: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TrackCreateResponse(BaseModel):
    track_id: int
    job_id: int
    status: str