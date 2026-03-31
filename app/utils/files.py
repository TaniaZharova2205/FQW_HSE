from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


def ensure_storage_dir() -> Path:
    storage_path = Path(settings.AUDIO_DOWNLOAD_DIR)
    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path


def build_unique_filename(original_name: str) -> str:
    suffix = Path(original_name).suffix or ".mp3"
    return f"{uuid4().hex}{suffix}"


def save_upload_file(upload_file: UploadFile) -> str:
    storage_path = ensure_storage_dir()
    filename = build_unique_filename(upload_file.filename or "audio.mp3")
    full_path = storage_path / filename

    with full_path.open("wb") as f:
        content = upload_file.file.read()
        f.write(content)

    return str(full_path)