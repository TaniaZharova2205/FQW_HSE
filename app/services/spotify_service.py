from dataclasses import dataclass

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from app.core.config import settings


@dataclass
class SpotifyTrackMeta:
    artist: str
    title: str
    full_name: str
    spotify_url: str


class SpotifyService:
    def __init__(self) -> None:
        auth_manager = SpotifyClientCredentials(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
        )
        self.client = spotipy.Spotify(client_credentials_manager=auth_manager)

    @staticmethod
    def extract_track_id(url: str) -> str:
        if "track/" not in url:
            raise ValueError("Invalid Spotify track URL")
        return url.split("track/")[1].split("?")[0]

    def get_track_meta(self, url: str) -> SpotifyTrackMeta:
        track_id = self.extract_track_id(url)
        result = self.client.track(track_id)

        artists = ", ".join(artist["name"] for artist in result["artists"])
        title = result["name"]
        full_name = f"{artists} - {title}"

        spotify_url = result.get("external_urls", {}).get("spotify", url)

        return SpotifyTrackMeta(
            artist=artists,
            title=title,
            full_name=full_name,
            spotify_url=spotify_url,
        )