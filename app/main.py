from pathlib import Path

import redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.tracks import router as tracks_router
from app.api.routes.results import router as results_router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(tracks_router, prefix=settings.API_V1_STR)
app.include_router(jobs_router, prefix=settings.API_V1_STR)
app.include_router(results_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
def startup_event():
    Path(settings.AUDIO_DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)


@app.get("/")
def root():
    return {"message": "Music Analyzer API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/redis")
def health_redis():
    r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
    return {"redis_ping": r.ping()}