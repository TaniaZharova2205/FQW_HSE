from datetime import datetime
from pydantic import BaseModel, ConfigDict


class JobRead(BaseModel):
    id: int
    track_id: int
    status: str
    progress: int
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)