from pathlib import Path
import os
import socket
import yt_dlp

from app.core.config import settings


class AudioDownloadError(Exception):
    pass


class DownloaderService:
    def __init__(self) -> None:
        self.download_dir = Path(settings.AUDIO_DOWNLOAD_DIR)
        self.download_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def sanitize_filename(name: str) -> str:
        forbidden = '<>:"/\\|?*'
        sanitized = "".join("_" if ch in forbidden else ch for ch in name)
        return sanitized.strip().rstrip(".")

    @staticmethod
    def check_dns(host: str = "www.youtube.com") -> None:
        try:
            socket.gethostbyname(host)
        except Exception as e:
            raise AudioDownloadError(f"DNS resolution failed for {host}: {e}") from e

    def download_by_search(self, query: str) -> str:
        self.check_dns()

        safe_name = self.sanitize_filename(query)
        output_template = str(self.download_dir / f"{safe_name}.%(ext)s")

        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "outtmpl": output_template,
            "quiet": True,
            "default_search": "ytsearch",
            "noplaylist": True,
            "extract_flat": False,
            "verbose": True,
        }

        if settings.YT_COOKIES_FILE and os.path.exists(settings.YT_COOKIES_FILE):
            ydl_opts["cookiefile"] = settings.YT_COOKIES_FILE

        if settings.FFMPEG_PATH:
            ydl_opts["ffmpeg_location"] = settings.FFMPEG_PATH

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch1:{query}", download=True)

                entries = info.get("entries")
                if entries:
                    first_entry = entries[0]
                    requested_title = first_entry.get("title") or safe_name
                else:
                    requested_title = info.get("title") or safe_name

                final_mp3 = self.download_dir / f"{self.sanitize_filename(requested_title)}.mp3"
                if final_mp3.exists():
                    return str(final_mp3)

                fallback_mp3 = self.download_dir / f"{safe_name}.mp3"
                if fallback_mp3.exists():
                    return str(fallback_mp3)

                candidates = list(self.download_dir.glob("*.mp3"))
                if candidates:
                    latest = max(candidates, key=lambda p: p.stat().st_mtime)
                    return str(latest)

                raise AudioDownloadError("MP3 file was not found after download")
        except Exception as e:
            raise AudioDownloadError(f"Download failed: {e}") from e