from sqlalchemy.orm import Session

from app.db.models import AnalysisResult, Track


def get_result_by_track_id(db: Session, track_id: int) -> AnalysisResult | None:
    return db.query(AnalysisResult).filter(AnalysisResult.track_id == track_id).first()


def get_or_create_result(db: Session, track: Track) -> AnalysisResult:
    result = get_result_by_track_id(db, track.id)
    if result is None:
        result = AnalysisResult(track_id=track.id)
        db.add(result)
        db.commit()
        db.refresh(result)
    return result


def upsert_transcription(
    db: Session,
    track: Track,
    transcription: str,
) -> AnalysisResult:
    result = get_or_create_result(db, track)
    result.transcription = transcription
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def upsert_genres(
    db: Session,
    track: Track,
    top_genres: list[dict],
) -> AnalysisResult:
    result = get_or_create_result(db, track)
    result.top_genres = top_genres

    if top_genres:
        result.genre = top_genres[0]["label"]
        result.genre_confidence = top_genres[0]["score"]

    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def upsert_moods(
    db: Session,
    track: Track,
    top_moods: list[dict],
) -> AnalysisResult:
    result = get_or_create_result(db, track)
    result.top_moods = top_moods

    if top_moods:
        result.mood = top_moods[0]["label"]
        result.mood_confidence = top_moods[0]["score"]

    db.add(result)
    db.commit()
    db.refresh(result)
    return result