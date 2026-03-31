import json
import time

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models import AnalysisJob, Track
from app.services.redis_service import get_redis_client, cache_job_status
from app.services.spotify_service import SpotifyService
from app.services.downloader_service import DownloaderService
from app.services.track_service import update_track_metadata_and_audio
from app.services.transcription_service import TranscriptionService
from app.services.genre_service import GenreService
from app.services.mood_service import MoodService
from app.services.result_service import (
    upsert_transcription,
    upsert_genres,
    upsert_moods,
)

QUEUE_NAME = "analysis_jobs"


def update_job(
    db: Session,
    job: AnalysisJob,
    *,
    status: str | None = None,
    progress: int | None = None,
    error_message: str | None = None,
) -> None:
    if status is not None:
        job.status = status
    if progress is not None:
        job.progress = progress
    if error_message is not None:
        job.error_message = error_message

    db.add(job)
    db.commit()
    db.refresh(job)
    cache_job_status(job.id, job.status, job.progress)


def process_spotify_track(db: Session, job: AnalysisJob, track: Track) -> None:
    spotify_service = SpotifyService()
    downloader = DownloaderService()

    meta = spotify_service.get_track_meta(track.spotify_url)
    update_job(db, job, progress=20)

    audio_path = downloader.download_by_search(meta.full_name)
    update_job(db, job, progress=35)

    update_track_metadata_and_audio(
        db=db,
        track=track,
        artist=meta.artist,
        title=meta.title,
        audio_path=audio_path,
    )


def process_transcription(db: Session, job: AnalysisJob, track: Track) -> str:
    if not track.audio_path:
        raise ValueError("Track audio_path is empty")

    transcription_service = TranscriptionService()
    update_job(db, job, progress=50)

    text = transcription_service.transcribe_track(
        audio_path=track.audio_path,
        track_title=track.title,
        artist=track.artist,
    )

    upsert_transcription(
        db=db,
        track=track,
        transcription=text,
    )

    update_job(db, job, progress=70)
    return text


def process_genre(db: Session, job: AnalysisJob, track: Track) -> None:
    if not track.audio_path:
        raise ValueError("Track audio_path is empty")

    genre_service = GenreService()
    top_genres = genre_service.predict_top3(track.audio_path)

    upsert_genres(
        db=db,
        track=track,
        top_genres=top_genres,
    )

    update_job(db, job, progress=85)


def process_mood(db: Session, job: AnalysisJob, track: Track, text: str) -> None:
    mood_service = MoodService()
    top_moods = mood_service.predict_top3(text)

    upsert_moods(
        db=db,
        track=track,
        top_moods=top_moods,
    )

    update_job(db, job, progress=95)


def worker_loop() -> None:
    redis_client = get_redis_client()

    while True:
        try:
            item = redis_client.blpop(QUEUE_NAME, timeout=5)
            if not item:
                continue

            _, raw_payload = item
            payload = json.loads(raw_payload)

            db = SessionLocal()
            try:
                job = db.query(AnalysisJob).filter(AnalysisJob.id == payload["job_id"]).first()
                if not job:
                    continue

                track = db.query(Track).filter(Track.id == payload["track_id"]).first()
                if not track:
                    update_job(db, job, status="failed", error_message="Track not found")
                    continue

                update_job(db, job, status="processing", progress=5)

                if track.source_type == "spotify":
                    process_spotify_track(db, job, track)
                    db.refresh(track)

                text = process_transcription(db, job, track)
                process_genre(db, job, track)
                process_mood(db, job, track, text)

                update_job(db, job, status="done", progress=100)

            except Exception as e:
                if "job" in locals() and job:
                    update_job(db, job, status="failed", error_message=str(e))
            finally:
                db.close()

        except Exception as e:
            print(f"Worker loop error: {e}")
            time.sleep(2)


def preload_models() -> None:
    print("[worker] Preloading models into memory...")
    TranscriptionService()
    GenreService()
    MoodService()
    print("[worker] Models loaded into memory.")

if __name__ == "__main__":
    preload_models()
    worker_loop()