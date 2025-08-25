from typing import Any, Dict, Optional
from datetime import datetime
import json
import uuid
import os
from loguru import logger
from contextlib import suppress

with suppress(Exception):
    import redis as _redis

class MockRedis:
    """Mock Redis client for development/testing"""
    
    def __init__(self):
        self.data = {}
        self.jobs = {}
    
    def ping(self) -> bool:
        """Mock ping"""
        return True
    
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Mock set"""
        self.data[key] = {
            'value': value,
            'expires_at': datetime.utcnow().timestamp() + ex if ex else None
        }
        return True
    
    def get(self, key: str) -> Optional[str]:
        """Mock get"""
        if key in self.data:
            item = self.data[key]
            if item['expires_at'] and datetime.utcnow().timestamp() > item['expires_at']:
                del self.data[key]
                return None
            return item['value']
        return None
    
    def delete(self, key: str) -> int:
        """Mock delete"""
        if key in self.data:
            del self.data[key]
            return 1
        return 0
    
    def lpush(self, key: str, value: Any) -> int:
        """Mock lpush"""
        if key not in self.data:
            self.data[key] = {'value': [], 'expires_at': None}
        self.data[key]['value'].insert(0, value)
        return len(self.data[key]['value'])

class BaseJobsClient:
    def _serialize_dates(self, obj):
        if isinstance(obj, dict):
            return {k: self._serialize_dates(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_dates(item) for item in obj]
        elif hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            return obj

class MockRedisClient(BaseJobsClient):
    """Mock Redis client for job management"""

    def __init__(self):
        self.redis = MockRedis()
        logger.info("Initialized mock Redis client")

    def health_check(self) -> Dict[str, Any]:
        try:
            self.redis.ping()
            return {"status": "healthy", "connected": True, "type": "mock"}
        except Exception as e:
            return {"status": "unhealthy", "connected": False, "error": str(e)}

    def create_job(self, job_type: str, payload: Dict[str, Any], user_id: str) -> str:
        job_id = str(uuid.uuid4())
        serialized_payload = self._serialize_dates(payload)
        job_data = {
            "id": job_id,
            "type": job_type,
            "status": "queued",
            "payload": serialized_payload,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        self.redis.set(f"job:{job_id}", json.dumps(job_data))
        self.redis.lpush(f"queue:{job_type}", job_id)
        logger.info(f"Created mock job {job_id} of type {job_type}")
        return job_id

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        job_data = self.redis.get(f"job:{job_id}")
        if job_data:
            return json.loads(job_data)
        return None

    def update_job_status(self, job_id: str, status: str, result: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        job_data = self.redis.get(f"job:{job_id}")
        if job_data:
            job_info = json.loads(job_data)
            job_info["status"] = status
            job_info["updated_at"] = datetime.utcnow().isoformat()
            if result:
                job_info["result"] = result
            if error:
                job_info["error"] = error
            self.redis.set(f"job:{job_id}", json.dumps(job_info))
            logger.info(f"Updated job {job_id} status to {status}")

class RealRedisClient(BaseJobsClient):
    """Real Redis client using redis-py."""

    def __init__(self):
        url = os.getenv("REDIS_URL", "redis://localhost:6379")
        if "_redis" not in globals():
            raise RuntimeError("redis library not available")
        self.redis = _redis.from_url(url, decode_responses=True)
        # test
        self.redis.ping()
        logger.info(f"Connected to Redis at {url}")

    def health_check(self) -> Dict[str, Any]:
        try:
            self.redis.ping()
            return {"status": "healthy", "connected": True, "type": "real"}
        except Exception as e:
            return {"status": "unhealthy", "connected": False, "error": str(e)}

    def create_job(self, job_type: str, payload: Dict[str, Any], user_id: str) -> str:
        job_id = str(uuid.uuid4())
        serialized_payload = self._serialize_dates(payload)
        job_data = {
            "id": job_id,
            "type": job_type,
            "status": "queued",
            "payload": serialized_payload,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        self.redis.set(f"job:{job_id}", json.dumps(job_data))
        self.redis.lpush(f"queue:{job_type}", job_id)
        logger.info(f"Created job {job_id} of type {job_type}")
        return job_id

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        job_data = self.redis.get(f"job:{job_id}")
        return json.loads(job_data) if job_data else None

    def update_job_status(self, job_id: str, status: str, result: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        job_data = self.redis.get(f"job:{job_id}")
        if not job_data:
            return
        job_info = json.loads(job_data)
        job_info["status"] = status
        job_info["updated_at"] = datetime.utcnow().isoformat()
        if result:
            job_info["result"] = result
        if error:
            job_info["error"] = error
        self.redis.set(f"job:{job_id}", json.dumps(job_info))
        logger.info(f"Updated job {job_id} status to {status}")

# Create singleton instance based on environment
def _create_redis_client():
    env = os.getenv("ENVIRONMENT", "development").lower()
    use_mock = os.getenv("USE_MOCK_REDIS", "").lower() in {"1", "true", "yes"}
    if env == "production" and not use_mock:
        try:
            return RealRedisClient()
        except Exception as e:
            logger.error(f"Failed to init real Redis client, falling back to mock: {e}")
            return MockRedisClient()
    return MockRedisClient()

redis_client = _create_redis_client()
