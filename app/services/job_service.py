from sqlalchemy.orm import Session

from app.db.models import AnalysisJob, Track
from app.services.redis_service import publish_job, cache_job_status


def create_analysis_job(db: Session, track: Track) -> AnalysisJob:
    job = AnalysisJob(
        track_id=track.id,
        status="pending",
        progress=0,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    cache_job_status(job.id, status=job.status, progress=job.progress)

    publish_job(
        {
            "job_id": job.id,
            "track_id": track.id,
            "source_type": track.source_type,
            "audio_path": track.audio_path,
            "spotify_url": track.spotify_url,
        }
    )

    return job


def get_job_by_id(db: Session, job_id: int) -> AnalysisJob | None:
    return db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()