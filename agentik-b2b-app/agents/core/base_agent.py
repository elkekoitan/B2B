from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable
from loguru import logger
import asyncio
import json
import time
import uuid
from datetime import datetime

class BaseAgent(ABC):
    """Base class for all agents in the system with Redis integration and error handling"""
    
    def __init__(self, name: str, description: str = "", max_retries: int = 3, retry_delay: float = 1.0):
        self.name = name
        self.description = description
        self.status = "initialized"
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.processed_tasks = 0
        self.failed_tasks = 0
        self.start_time = None
        self.redis_client = None
        
    @abstractmethod
    async def process_task(self, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a task assigned to this agent"""
        pass
        
    async def initialize(self):
        """Initialize agent resources including Redis connection"""
        from core.redis_client import get_redis
        
        self.redis_client = get_redis()
        self.status = "active"
        self.start_time = time.time()
        logger.info(f"Agent {self.name} initialized with Redis connection")
        
    async def cleanup(self):
        """Cleanup agent resources"""
        self.status = "inactive"
        logger.info(f"Agent {self.name} cleaned up. Tasks processed: {self.processed_tasks}, Failed: {self.failed_tasks}")
        
    async def execute_with_retry(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task with retry logic and error handling"""
        task_id = task_data.get('task_id', str(uuid.uuid4()))
        
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Agent {self.name} - Processing task {task_id} (attempt {attempt}/{self.max_retries})")
                
                result = await self.process_task(task_data)
                
                if result and not result.get('error'):
                    self.processed_tasks += 1
                    await self.log_task_result(task_data, result, True)
                    return result
                else:
                    error_msg = result.get('error', 'Unknown error') if result else 'No result returned'
                    logger.error(f"Agent {self.name} - Task {task_id} failed: {error_msg}")
                    
                    if attempt == self.max_retries:
                        self.failed_tasks += 1
                        await self.log_task_result(task_data, result or {'error': error_msg}, False)
                        return {'error': error_msg, 'attempts': attempt}
                    
            except Exception as e:
                logger.error(f"Agent {self.name} - Task {task_id} exception on attempt {attempt}: {e}")
                
                if attempt == self.max_retries:
                    self.failed_tasks += 1
                    error_result = {'error': str(e), 'attempts': attempt}
                    await self.log_task_result(task_data, error_result, False)
                    return error_result
                    
            # Wait before retry
            if attempt < self.max_retries:
                await asyncio.sleep(self.retry_delay * attempt)
                
        return {'error': 'Max retries exceeded'}
        
    async def log_task_result(self, task_data: Dict[str, Any], result: Dict[str, Any], success: bool = True):
        """Log the result of a task to Redis and local logs"""
        task_id = task_data.get('task_id', 'unknown')
        status = "SUCCESS" if success else "FAILED"
        
        # Local logging
        logger.info(f"Agent {self.name} - Task {status}: {task_id}")
        
        if not success and result.get('error'):
            logger.error(f"Agent {self.name} - Error: {result['error']}")
        
        # Redis logging if available
        if self.redis_client:
            try:
                log_entry = {
                    'agent_name': self.name,
                    'task_id': task_id,
                    'status': status,
                    'timestamp': datetime.utcnow().isoformat(),
                    'result': result,
                    'task_data': task_data
                }
                
                await self.redis_client.lpush(
                    f"agent_logs_{self.name}",
                    json.dumps(log_entry)
                )
                
                # Keep only last 100 logs per agent
                await self.redis_client.ltrim(f"agent_logs_{self.name}", 0, 99)
                
            except Exception as e:
                logger.error(f"Failed to log to Redis: {e}")
    
    async def queue_task(self, target_agent: str, task_data: Dict[str, Any]) -> bool:
        """Queue a task for another agent"""
        if not self.redis_client:
            logger.error(f"Agent {self.name} - Redis client not available for queuing task")
            return False
            
        try:
            task_data['queued_by'] = self.name
            task_data['queued_at'] = datetime.utcnow().isoformat()
            
            if 'task_id' not in task_data:
                task_data['task_id'] = str(uuid.uuid4())
            
            queue_name = f"agent_{target_agent}_queue"
            await self.redis_client.lpush(queue_name, json.dumps(task_data))
            
            logger.info(f"Agent {self.name} - Queued task {task_data['task_id']} for {target_agent}")
            return True
            
        except Exception as e:
            logger.error(f"Agent {self.name} - Error queuing task: {e}")
            return False
    
    async def publish_status_update(self, status_data: Dict[str, Any]):
        """Publish status update to Redis pub/sub"""
        if not self.redis_client:
            return
            
        try:
            status_update = {
                'agent_name': self.name,
                'timestamp': datetime.utcnow().isoformat(),
                'status': self.status,
                'processed_tasks': self.processed_tasks,
                'failed_tasks': self.failed_tasks,
                **status_data
            }
            
            await self.redis_client.publish(
                'agent_status_updates',
                json.dumps(status_update)
            )
            
        except Exception as e:
            logger.error(f"Failed to publish status update: {e}")
            
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status with metrics"""
        uptime = time.time() - self.start_time if self.start_time else 0
        
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "processed_tasks": self.processed_tasks,
            "failed_tasks": self.failed_tasks,
            "uptime_seconds": uptime,
            "success_rate": (self.processed_tasks / max(1, self.processed_tasks + self.failed_tasks)) * 100
        }