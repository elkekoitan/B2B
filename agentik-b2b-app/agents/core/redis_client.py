import redis.asyncio as redis
import os
from loguru import logger
import asyncio
from typing import Optional

# Global Redis client
redis_client = None

async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    try:
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        redis_client = redis.from_url(redis_url, decode_responses=True)
        
        # Test connection with timeout
        await asyncio.wait_for(redis_client.ping(), timeout=5.0)
        logger.info("Redis connection initialized successfully")
        return redis_client
    except asyncio.TimeoutError:
        logger.error("Redis connection timeout")
        raise
    except Exception as e:
        logger.error(f"Failed to initialize Redis connection: {e}")
        raise

def get_redis() -> Optional[redis.Redis]:
    """Get Redis client"""
    return redis_client

async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
        logger.info("Redis connection closed")

async def check_redis_health() -> bool:
    """Check Redis connection health"""
    global redis_client
    if not redis_client:
        return False
    
    try:
        await redis_client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return False

async def clear_agent_queues():
    """Clear all agent queues (useful for development)"""
    global redis_client
    if not redis_client:
        return
    
    try:
        # Get all queue keys
        queue_keys = await redis_client.keys('agent_*_queue')
        
        if queue_keys:
            await redis_client.delete(*queue_keys)
            logger.info(f"Cleared {len(queue_keys)} agent queues")
        
    except Exception as e:
        logger.error(f"Error clearing agent queues: {e}")