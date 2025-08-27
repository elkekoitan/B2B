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
    
    def lrem(self, key: str, count: int, value: Any) -> int:
        if key not in self.data or not isinstance(self.data[key].get('value'), list):
            return 0
        arr = self.data[key]['value']
        removed = 0
        # count=0 remove all occurrences
        if count == 0:
            new_arr = [x for x in arr if x != value]
            removed = len(arr) - len(new_arr)
            self.data[key]['value'] = new_arr
            return removed
        # positive: first N
        direction = 1 if count > 0 else -1
        cnt = abs(count)
        idxs = []
        rng = range(len(arr)) if direction == 1 else range(len(arr)-1, -1, -1)
        for i in rng:
            if arr[i] == value:
                idxs.append(i)
                removed += 1
                if removed >= cnt:
                    break
        for i in sorted(idxs, reverse=True):
            arr.pop(i)
        return removed
    
    def lrange(self, key: str, start: int, end: int):
        arr = []
        if key in self.data and isinstance(self.data[key].get('value'), list):
            arr = self.data[key]['value']
        # Emulate Redis inclusive end where -1 means end of list
        if end == -1:
            end = len(arr) - 1
        return arr[start:end+1] if arr else []
    
    def llen(self, key: str) -> int:
        if key in self.data and isinstance(self.data[key].get('value'), list):
            return len(self.data[key]['value'])
        return 0
    
    def hset(self, key: str, mapping: Dict[str, Any]):
        if key not in self.data:
            self.data[key] = {'value': {}, 'expires_at': None}
        # store all as strings to mimic Redis behavior roughly
        for k, v in mapping.items():
            self.data[key]['value'][k] = v
        return True
    
    def hgetall(self, key: str) -> Dict[str, Any]:
        if key in self.data and isinstance(self.data[key].get('value'), dict):
            return dict(self.data[key]['value'])
        return {}

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
    # extension points
    def record_user_job(self, user_id: str, job_id: str):
        raise NotImplementedError
    def list_user_jobs(self, user_id: str, limit: int = 10):
        raise NotImplementedError

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
        now = datetime.utcnow().isoformat()
        job_envelope = {
            "job_id": job_id,
            "job_type": job_type,
            "user_id": user_id,
            "payload": serialized_payload,
            "created_at": now,
            "updated_at": now,
        }
        # Push to unified agent queue
        self.redis.lpush("agentik:jobs", json.dumps(job_envelope))
        # Initialize status hash
        self.redis.hset(f"agentik:status:{job_id}", {
            "status": "queued",
            "created_at": now,
            "updated_at": now,
            "user_id": user_id,
        })
        # Back-compat simple job store
        self.redis.set(f"job:{job_id}", json.dumps(job_envelope))
        logger.info(f"Created mock job {job_id} of type {job_type}")
        return job_id

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        # Prefer agentik status hash
        st = self.redis.hgetall(f"agentik:status:{job_id}")
        if st:
            result = st.get("result")
            parsed_result = None
            try:
                parsed_result = json.loads(result) if isinstance(result, str) else result
            except Exception:
                parsed_result = result
            payload = self.redis.get(f"job:{job_id}")
            job_env = json.loads(payload) if payload else {}
            job_type = job_env.get("job_type")
            user_id = st.get("user_id")
            return {
                "job_id": job_id,
                "status": st.get("status", "unknown"),
                "created_at": st.get("created_at"),
                "updated_at": st.get("updated_at"),
                "job_type": job_type,
                "result": parsed_result,
                "error": st.get("error"),
                "user_id": user_id,
                "data": {"user_id": user_id, "payload": job_env if payload else None},
            }
        # Fallback to legacy job record
        job_data = self.redis.get(f"job:{job_id}")
        if job_data:
            jd = json.loads(job_data)
            return {
                "job_id": jd.get("job_id") or jd.get("id", job_id),
                "status": jd.get("status", "queued"),
                "created_at": jd.get("created_at"),
                "updated_at": jd.get("updated_at"),
                "job_type": jd.get("job_type"),
                "result": jd.get("result"),
                "error": jd.get("error"),
                "user_id": jd.get("user_id"),
                "data": {"user_id": jd.get("user_id")},
            }
        return None

    def update_job_status(self, job_id: str, status: str, result: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        now = datetime.utcnow().isoformat()
        mapping = {"status": status, "updated_at": now}
        if result is not None:
            mapping["result"] = json.dumps(result)
        if error is not None:
            mapping["error"] = error
        self.redis.hset(f"agentik:status:{job_id}", mapping)
        # Mirror in legacy record for compatibility if exists
        job_data = self.redis.get(f"job:{job_id}")
        if job_data:
            job_info = json.loads(job_data)
            job_info["status"] = status
            job_info["updated_at"] = now
            if result is not None:
                job_info["result"] = result
            if error is not None:
                job_info["error"] = error
            self.redis.set(f"job:{job_id}", json.dumps(job_info))
        logger.info(f"Updated job {job_id} status to {status}")

    def cancel_job(self, job_id: str) -> bool:
        # Try remove from main queue
        env_str = self.redis.get(f"job:{job_id}")
        removed = 0
        if env_str:
            removed = self.redis.lrem("agentik:jobs", 0, env_str)
        # Mark status as failed/cancelled
        self.update_job_status(job_id, "failed", error="cancelled by user")
        return removed > 0

    def record_user_job(self, user_id: str, job_id: str):
        key = f"user:{user_id}:jobs"
        if key not in self.redis.data:
            self.redis.data[key] = { 'value': [], 'expires_at': None }
        self.redis.data[key]['value'].insert(0, job_id)
        return True

    def list_user_jobs(self, user_id: str, limit: int = 10):
        key = f"user:{user_id}:jobs"
        ids = []
        if key in self.redis.data and isinstance(self.redis.data[key].get('value'), list):
            ids = list(self.redis.data[key]['value'])[:limit]
        jobs = []
        for jid in ids:
            st = self.get_job_status(jid)
            if st:
                jobs.append(st)
        return jobs

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
        now = datetime.utcnow().isoformat()
        job_envelope = {
            "job_id": job_id,
            "job_type": job_type,
            "user_id": user_id,
            "payload": serialized_payload,
            "created_at": now,
            "updated_at": now,
        }
        self.redis.lpush("agentik:jobs", json.dumps(job_envelope))
        self.redis.hset(f"agentik:status:{job_id}", {
            "status": "queued",
            "created_at": now,
            "updated_at": now,
            "user_id": user_id,
        })
        # Back-compat legacy record
        self.redis.set(f"job:{job_id}", json.dumps(job_envelope))
        logger.info(f"Created job {job_id} of type {job_type}")
        return job_id

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        st = self.redis.hgetall(f"agentik:status:{job_id}")
        if st:
            result = st.get("result")
            parsed_result = None
            try:
                parsed_result = json.loads(result) if isinstance(result, str) else result
            except Exception:
                parsed_result = result
            payload = self.redis.get(f"job:{job_id}")
            job_env = json.loads(payload) if payload else {}
            job_type = job_env.get("job_type")
            user_id = st.get("user_id")
            return {
                "job_id": job_id,
                "status": st.get("status", "unknown"),
                "created_at": st.get("created_at"),
                "updated_at": st.get("updated_at"),
                "job_type": job_type,
                "result": parsed_result,
                "error": st.get("error"),
                "user_id": user_id,
                "data": {"user_id": user_id, "payload": job_env if payload else None},
            }
        job_data = self.redis.get(f"job:{job_id}")
        if job_data:
            jd = json.loads(job_data)
            return {
                "job_id": jd.get("job_id") or jd.get("id", job_id),
                "status": jd.get("status", "queued"),
                "created_at": jd.get("created_at"),
                "updated_at": jd.get("updated_at"),
                "job_type": jd.get("job_type"),
                "result": jd.get("result"),
                "error": jd.get("error"),
                "user_id": jd.get("user_id"),
                "data": {"user_id": jd.get("user_id")},
            }
        return None

    def update_job_status(self, job_id: str, status: str, result: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        now = datetime.utcnow().isoformat()
        mapping = {"status": status, "updated_at": now}
        if result is not None:
            mapping["result"] = json.dumps(result)
        if error is not None:
            mapping["error"] = error
        self.redis.hset(f"agentik:status:{job_id}", mapping)
        job_data = self.redis.get(f"job:{job_id}")
        if job_data:
            job_info = json.loads(job_data)
            job_info["status"] = status
            job_info["updated_at"] = now
            if result is not None:
                job_info["result"] = result
            if error is not None:
                job_info["error"] = error
            self.redis.set(f"job:{job_id}", json.dumps(job_info))
        logger.info(f"Updated job {job_id} status to {status}")

    def cancel_job(self, job_id: str) -> bool:
        env_str = self.redis.get(f"job:{job_id}")
        removed = 0
        if env_str:
            try:
                removed = self.redis.lrem("agentik:jobs", 0, env_str)
            except Exception as e:
                logger.warning(f"lrem failed: {e}")
        self.update_job_status(job_id, "failed", error="cancelled by user")
        return removed > 0

    def record_user_job(self, user_id: str, job_id: str):
        key = f"user:{user_id}:jobs"
        self.redis.lpush(key, job_id)
        return True

    def list_user_jobs(self, user_id: str, limit: int = 10):
        key = f"user:{user_id}:jobs"
        ids = self.redis.lrange(key, 0, max(0, limit - 1)) or []
        jobs = []
        for jid in ids:
            st = self.get_job_status(jid)
            if st:
                jobs.append(st)
        return jobs

# Create singleton instance based on environment
def _create_redis_client():
    # Always use real Redis client; do not fallback to mock
    try:
        return RealRedisClient()
    except Exception as e:
        logger.error(f"Failed to init Redis client: {e}")
        raise

redis_client = _create_redis_client()
