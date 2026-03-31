from sqlalchemy.orm import Session

from app.db.models import Track, User


def create_uploaded_track(
    db: Session,
    user: User,
    original_filename: str,
    audio_path: str,
) -> Track:
    track = Track(
        user_id=user.id,
        source_type="upload",
        original_filename=original_filename,
        audio_path=audio_path,
    )
    db.add(track)
    db.commit()
    db.refresh(track)
    return track


def create_spotify_track(
    db: Session,
    user: User,
    spotify_url: str,
) -> Track:
    track = Track(
        user_id=user.id,
        source_type="spotify",
        spotify_url=spotify_url,
    )
    db.add(track)
    db.commit()
    db.refresh(track)
    return track


def get_track_by_id(db: Session, track_id: int) -> Track | None:
    return db.query(Track).filter(Track.id == track_id).first()


def get_tracks_by_user_id(db: Session, user_id: int) -> list[Track]:
    return (
        db.query(Track)
        .filter(Track.user_id == user_id)
        .order_by(Track.created_at.desc())
        .all()
    )


def update_track_metadata_and_audio(
    db: Session,
    track: Track,
    artist: str,
    title: str,
    audio_path: str,
) -> Track:
    track.artist = artist
    track.title = title
    track.audio_path = audio_path
    db.add(track)
    db.commit()
    db.refresh(track)
    return track