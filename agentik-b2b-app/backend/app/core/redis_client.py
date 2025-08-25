import redis.asyncio as redis
from app.core.config import settings
from loguru import logger
from typing import Optional
import json
import pickle

# Global Redis client
redis_client: Optional[redis.Redis] = None

async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=False  # We'll handle encoding manually for flexibility
        )
        
        # Test connection
        await redis_client.ping()
        logger.info("Redis connection initialized successfully")
        return redis_client
    except Exception as e:
        logger.error(f"Failed to initialize Redis connection: {e}")
        raise

def get_redis() -> redis.Redis:
    """Get Redis client dependency"""
    return redis_client

class RedisService:
    """Redis service for caching and queue operations"""
    
    @staticmethod
    async def set_json(key: str, value: dict, expire: int = 3600):
        """Store JSON data in Redis with expiration"""
        try:
            json_data = json.dumps(value)
            await redis_client.set(key, json_data, ex=expire)
            return True
        except Exception as e:
            logger.error(f"Error storing JSON in Redis: {e}")
            return False
    
    @staticmethod
    async def get_json(key: str) -> Optional[dict]:
        """Retrieve JSON data from Redis"""
        try:
            data = await redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error retrieving JSON from Redis: {e}")
            return None
    
    @staticmethod
    async def delete(key: str):
        """Delete key from Redis"""
        try:
            await redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting key from Redis: {e}")
            return False
    
    @staticmethod
    async def enqueue_task(queue_name: str, task_data: dict):
        """Add task to queue"""
        try:
            task_json = json.dumps(task_data)
            await redis_client.lpush(queue_name, task_json)
            logger.info(f"Task enqueued to {queue_name}: {task_data}")
            return True
        except Exception as e:
            logger.error(f"Error enqueuing task: {e}")
            return False
    
    @staticmethod
    async def dequeue_task(queue_name: str) -> Optional[dict]:
        """Get task from queue"""
        try:
            task_json = await redis_client.brpop(queue_name, timeout=1)
            if task_json:
                return json.loads(task_json[1])
            return None
        except Exception as e:
            logger.error(f"Error dequeuing task: {e}")
            return None