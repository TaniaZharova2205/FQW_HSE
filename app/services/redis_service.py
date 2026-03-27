import json
import redis

from app.core.config import settings

QUEUE_NAME = "analysis_jobs"


def get_redis_client() -> redis.Redis:
    return redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


def publish_job(payload: dict) -> None:
    client = get_redis_client()
    client.rpush(QUEUE_NAME, json.dumps(payload))


def cache_job_status(job_id: int, status: str, progress: int = 0) -> None:
    client = get_redis_client()
    client.hset(
        f"job:{job_id}",
        mapping={
            "status": status,
            "progress": progress,
        },
    )