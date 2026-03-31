from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models import User
from app.schemas.track import SpotifyTrackCreate, TrackCreateResponse, TrackRead
from app.services.job_service import create_analysis_job
from app.services.track_service import (
    create_spotify_track,
    create_uploaded_track,
    get_track_by_id,
    get_tracks_by_user_id,
)
from app.utils.files import save_upload_file
from app.schemas.history import TrackHistoryItem
from app.services.history_service import get_user_analysis_history

router = APIRouter(prefix="/tracks", tags=["tracks"])


@router.get("", response_model=List[TrackRead])
def list_tracks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_tracks_by_user_id(db, current_user.id)


@router.post("/upload", response_model=TrackCreateResponse, status_code=status.HTTP_201_CREATED)
def upload_track(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is missing")

    allowed_extensions = {".mp3", ".wav", ".ogg", ".flac", ".m4a"}
    filename_lower = file.filename.lower()

    if not any(filename_lower.endswith(ext) for ext in allowed_extensions):
        raise HTTPException(status_code=400, detail="Unsupported audio format")

    saved_path = save_upload_file(file)

    track = create_uploaded_track(
        db=db,
        user=current_user,
        original_filename=file.filename,
        audio_path=saved_path,
    )
    job = create_analysis_job(db, track)

    return TrackCreateResponse(
        track_id=track.id,
        job_id=job.id,
        status=job.status,
    )


@router.post("/from-spotify", response_model=TrackCreateResponse, status_code=status.HTTP_201_CREATED)
def create_track_from_spotify(
    data: SpotifyTrackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if "open.spotify.com/track/" not in str(data.spotify_url):
        raise HTTPException(status_code=400, detail="Invalid Spotify track URL")

    track = create_spotify_track(
        db=db,
        user=current_user,
        spotify_url=str(data.spotify_url),
    )
    job = create_analysis_job(db, track)

    return TrackCreateResponse(
        track_id=track.id,
        job_id=job.id,
        status=job.status,
    )
    

@router.get("/history", response_model=list[TrackHistoryItem])
def get_tracks_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_analysis_history(db, current_user.id)
    

@router.get("/{track_id}", response_model=TrackRead)
def get_track(
    track_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    track = get_track_by_id(db, track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    if track.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return track
