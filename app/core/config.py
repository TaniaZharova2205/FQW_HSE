from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Music Analyzer API"
    API_V1_STR: str = "/api/v1"

    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    AUDIO_DOWNLOAD_DIR: str = "/code/storage/music"

    MODELS_DIR: str = "/code/models"

    WHISPER_MODEL_ID: str = "openai/whisper-small"
    GENRE_MODEL_ID: str = "m3hrdadfi/wav2vec2-base-100k-gtzan-music-genres"
    MOOD_MODEL_ID: str = "Zharova/mood_model"

    WHISPER_MODEL_PATH: str = "/code/models/whisper"
    GENRE_MODEL_PATH: str = "/code/models/m3hrdadfi-wav2vec"
    MOOD_MODEL_PATH: str = "/code/models/mood_model"

    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str
    FFMPEG_PATH: str | None = None
    YT_COOKIES_FILE: str | None = None

    WHISPER_CHUNK_LENGTH_SEC: int = 30
    WHISPER_OVERLAP_SEC: int = 5
    HUGGING_FACE_TOKEN: str

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()