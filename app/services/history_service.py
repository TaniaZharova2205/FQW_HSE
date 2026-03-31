from sqlalchemy.orm import Session

from app.db.models import Track, AnalysisJob, AnalysisResult


def get_user_analysis_history(db: Session, user_id: int) -> list[dict]:
    tracks = (
        db.query(Track)
        .filter(Track.user_id == user_id)
        .order_by(Track.created_at.desc())
        .all()
    )

    history_items: list[dict] = []

    for track in tracks:
        latest_job = (
            db.query(AnalysisJob)
            .filter(AnalysisJob.track_id == track.id)
            .order_by(AnalysisJob.created_at.desc())
            .first()
        )

        result = (
            db.query(AnalysisResult)
            .filter(AnalysisResult.track_id == track.id)
            .first()
        )

        history_items.append(
            {
                "track_id": track.id,
                "artist": track.artist,
                "title": track.title,
                "source_type": track.source_type,
                "original_filename": track.original_filename,
                "spotify_url": track.spotify_url,

                "job_id": latest_job.id if latest_job else None,
                "job_status": latest_job.status if latest_job else None,
                "job_progress": latest_job.progress if latest_job else None,
                "job_error_message": latest_job.error_message if latest_job else None,

                "transcription": result.transcription if result else None,

                "genre": result.genre if result else None,
                "genre_confidence": result.genre_confidence if result else None,
                "top_genres": result.top_genres if result else None,

                "mood": result.mood if result else None,
                "mood_confidence": result.mood_confidence if result else None,
                "top_moods": result.top_moods if result else None,

                "created_at": track.created_at,
            }
        )

    return history_items