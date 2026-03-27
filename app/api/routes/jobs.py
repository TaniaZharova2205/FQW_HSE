from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models import User, Track
from app.schemas.job import JobRead
from app.services.job_service import get_job_by_id

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobRead)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    track = db.query(Track).filter(Track.id == job.track_id).first()
    if not track or track.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return job