from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models import AnalysisResult, Track, User
from app.schemas.result import AnalysisResultRead

router = APIRouter(prefix="/results", tags=["results"])


@router.get("/track/{track_id}", response_model=AnalysisResultRead)
def get_result_by_track_id(
    track_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    if track.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    result = db.query(AnalysisResult).filter(AnalysisResult.track_id == track_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found yet")

    return result