import json
import time

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models import AnalysisJob, Track
from app.services.redis_service import get_redis_client, cache_job_status
from app.services.spotify_service import SpotifyService
from app.services.downloader_service import DownloaderService
from app.services.track_service import update_track_metadata_and_audio

QUEUE_NAME = "analysis_jobs"


def set_job_processing(db: Session, job: AnalysisJob) -> None:
    job.status = "processing"
    job.progress = 10
    db.add(job)
    db.commit()
    cache_job_status(job.id, job.status, job.progress)


def set_job_done(db: Session, job: AnalysisJob) -> None:
    job.status = "done"
    job.progress = 100
    db.add(job)
    db.commit()
    cache_job_status(job.id, job.status, job.progress)


def set_job_failed(db: Session, job: AnalysisJob, error_message: str) -> None:
    job.status = "failed"
    job.error_message = error_message
    db.add(job)
    db.commit()
    cache_job_status(job.id, job.status, job.progress)


def process_spotify_track(db: Session, job: AnalysisJob, track: Track) -> None:
    spotify_service = SpotifyService()
    downloader = DownloaderService()

    meta = spotify_service.get_track_meta(track.spotify_url)
    job.progress = 30
    db.add(job)
    db.commit()
    cache_job_status(job.id, job.status, job.progress)

    audio_path = downloader.download_by_search(meta.full_name)
    job.progress = 70
    db.add(job)
    db.commit()
    cache_job_status(job.id, job.status, job.progress)

    update_track_metadata_and_audio(
        db=db,
        track=track,
        artist=meta.artist,
        title=meta.title,
        audio_path=audio_path,
    )


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
                    set_job_failed(db, job, "Track not found")
                    continue

                set_job_processing(db, job)

                if track.source_type == "spotify":
                    process_spotify_track(db, job, track)

                # здесь потом добавите:
                # transcription
                # genre
                # mood

                set_job_done(db, job)

            except Exception as e:
                if "job" in locals() and job:
                    set_job_failed(db, job, str(e))
            finally:
                db.close()

        except Exception as e:
            print(f"Worker loop error: {e}")
            time.sleep(2)


if __name__ == "__main__":
    worker_loop()