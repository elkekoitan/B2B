import asyncio
import redis.asyncio as redis
from typing import Dict, Any, Optional, List
from loguru import logger
from core.base_agent import BaseAgent
import json
import os
from datetime import datetime
from contextlib import asynccontextmanager

class AgentOrchestrator:
    """Enhanced orchestrator for managing and coordinating agents with full workflow support"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.redis_client: Optional[redis.Redis] = None
        self.running = False
        self.tasks = set()
        self.health_check_interval = 30  # seconds
        self.agent_status: Dict[str, Dict[str, Any]] = {}
        self.workflows: Dict[str, List[str]] = {}
        
        # Define agent workflows
        self._define_workflows()
        
    def _define_workflows(self):
        """Define agent workflow sequences"""
        self.workflows = {
            'rfq_processing': [
                'rfq_intake_agent',
                'supplier_discovery_agent', 
                'email_send_agent',
                'inbox_parser_agent',
                'supplier_verifier_agent',
                'aggregation_report_agent'
            ],
            'offer_processing': [
                'inbox_parser_agent',
                'supplier_verifier_agent', 
                'aggregation_report_agent'
            ],
            'daily_maintenance': [
                'aggregation_report_agent'
            ]
        }
        
    async def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.agents[agent.name] = agent
        self.agent_status[agent.name] = {
            'status': 'registered',
            'last_seen': datetime.utcnow().isoformat(),
            'tasks_processed': 0,
            'tasks_failed': 0
        }
        logger.info(f"Registered agent: {agent.name}")
        
    async def start(self):
        """Start the orchestrator and all agents"""
        self.running = True
        
        # Initialize Redis connection
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        
        # Test Redis connection
        try:
            await self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise
        
        # Initialize all agents
        for agent in self.agents.values():
            await agent.initialize()
            
        # Start all agent processing tasks
        for agent in self.agents.values():
            task = asyncio.create_task(self.run_agent(agent))
            self.tasks.add(task)
            task.add_done_callback(self.tasks.discard)
            
        # Start health check task
        health_task = asyncio.create_task(self.health_check_loop())
        self.tasks.add(health_task)
        health_task.add_done_callback(self.tasks.discard)
        
        # Start workflow monitor task
        workflow_task = asyncio.create_task(self.workflow_monitor_loop())
        self.tasks.add(workflow_task)
        workflow_task.add_done_callback(self.tasks.discard)
        
        logger.info(f"Started orchestrator with {len(self.agents)} agents")
        
    async def shutdown(self):
        """Graceful shutdown of all agents and the orchestrator"""
        logger.info("Starting orchestrator shutdown...")
        self.running = False
        
        # Cleanup all agents
        for agent in self.agents.values():
            try:
                await agent.cleanup()
            except Exception as e:
                logger.error(f"Error during agent {agent.name} cleanup: {e}")
        
        # Cancel all running tasks
        for task in self.tasks.copy():
            if not task.done():
                task.cancel()
                
        # Wait for all tasks to complete with timeout
        if self.tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self.tasks, return_exceptions=True),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                logger.warning("Some tasks didn't complete within timeout")
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
            
        logger.info("Orchestrator shutdown complete")
        
    async def run_agent(self, agent: BaseAgent):
        """Enhanced agent processing loop with error recovery"""
        logger.info(f"Starting agent: {agent.name}")
        
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while self.running:
            try:
                # Check for tasks in the agent's queue
                task_data = await self.get_task_for_agent(agent.name)
                
                if task_data:
                    logger.info(f"Agent {agent.name} processing task: {task_data.get('task_id', 'unknown')}")
                    
                    # Execute task with retry logic
                    result = await agent.execute_with_retry(task_data)
                    
                    # Update agent status
                    if result and not result.get('error'):
                        self.agent_status[agent.name]['tasks_processed'] += 1
                        consecutive_errors = 0
                    else:
                        self.agent_status[agent.name]['tasks_failed'] += 1
                        consecutive_errors += 1
                        
                    self.agent_status[agent.name]['last_seen'] = datetime.utcnow().isoformat()
                    
                    # Publish status update
                    await agent.publish_status_update({
                        'task_result': result,
                        'consecutive_errors': consecutive_errors
                    })
                    
                else:
                    # No tasks, sleep briefly and reset error counter
                    consecutive_errors = 0
                    await asyncio.sleep(1)
                    
                # If too many consecutive errors, pause the agent
                if consecutive_errors >= max_consecutive_errors:
                    logger.error(f"Agent {agent.name} has {consecutive_errors} consecutive errors. Pausing for 30 seconds.")
                    await asyncio.sleep(30)
                    consecutive_errors = 0
                    
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Critical error in agent {agent.name}: {e}")
                
                if consecutive_errors >= max_consecutive_errors:
                    logger.error(f"Agent {agent.name} failing repeatedly. Pausing for 60 seconds.")
                    await asyncio.sleep(60)
                    consecutive_errors = 0
                else:
                    await asyncio.sleep(5)
                    
    async def get_task_for_agent(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Enhanced task retrieval with multiple queue support"""
        if not self.redis_client:
            return None
            
        try:
            # Check multiple queue names for the agent
            queue_names = [
                f"agent_{agent_name}_queue",
                f"{agent_name.lower()}_queue",
                "general_queue"
            ]
            
            for queue_name in queue_names:
                # Use BRPOP with timeout for efficient blocking
                result = await self.redis_client.brpop([queue_name], timeout=1)
                if result:
                    queue, task_json = result
                    task_data = json.loads(task_json)
                    
                    # Add metadata
                    task_data['retrieved_from_queue'] = queue
                    task_data['retrieved_at'] = datetime.utcnow().isoformat()
                    
                    return task_data
                    
            return None
            
        except Exception as e:
            logger.error(f"Error getting task for agent {agent_name}: {e}")
            return None
            
    async def queue_task(self, agent_name: str, task_data: Dict[str, Any]) -> bool:
        """Enhanced task queuing with validation and monitoring"""
        if not self.redis_client:
            logger.error("Redis client not initialized")
            return False
            
        # Validate agent exists
        if agent_name not in self.agents:
            logger.error(f"Agent {agent_name} not registered")
            return False
            
        try:
            # Add metadata
            task_data['queued_at'] = datetime.utcnow().isoformat()
            task_data['queued_by'] = 'orchestrator'
            
            if 'task_id' not in task_data:
                task_data['task_id'] = f"{agent_name}_{datetime.utcnow().timestamp()}"
            
            queue_name = f"agent_{agent_name}_queue"
            task_json = json.dumps(task_data)
            
            await self.redis_client.lpush(queue_name, task_json)
            
            # Update queue stats
            await self.redis_client.incr(f"stats:queue:{queue_name}:total")
            
            logger.info(f"Queued task {task_data['task_id']} for agent {agent_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error queuing task for agent {agent_name}: {e}")
            return False
    
    async def execute_workflow(self, workflow_name: str, initial_data: Dict[str, Any]) -> bool:
        """Execute a predefined workflow"""
        if workflow_name not in self.workflows:
            logger.error(f"Workflow {workflow_name} not found")
            return False
            
        workflow_agents = self.workflows[workflow_name]
        
        logger.info(f"Starting workflow {workflow_name} with {len(workflow_agents)} agents")
        
        # Add workflow metadata
        workflow_data = initial_data.copy()
        workflow_data['workflow_name'] = workflow_name
        workflow_data['workflow_started_at'] = datetime.utcnow().isoformat()
        
        # Queue first agent in workflow
        first_agent = workflow_agents[0]
        success = await self.queue_task(first_agent, workflow_data)
        
        if success:
            logger.info(f"Workflow {workflow_name} started successfully")
        else:
            logger.error(f"Failed to start workflow {workflow_name}")
            
        return success
    
    async def health_check_loop(self):
        """Monitor agent health and system status"""
        while self.running:
            try:
                # Check Redis connection
                await self.redis_client.ping()
                
                # Update agent health status
                for agent_name in self.agents:
                    status = self.agent_status.get(agent_name, {})
                    
                    # Check if agent is responsive
                    last_seen = status.get('last_seen')
                    if last_seen:
                        last_seen_time = datetime.fromisoformat(last_seen)
                        time_since_last_seen = datetime.utcnow() - last_seen_time
                        
                        if time_since_last_seen.total_seconds() > 300:  # 5 minutes
                            logger.warning(f"Agent {agent_name} hasn't been seen for {time_since_last_seen}")
                            status['health'] = 'unhealthy'
                        else:
                            status['health'] = 'healthy'
                    else:
                        status['health'] = 'unknown'
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                await asyncio.sleep(self.health_check_interval)
    
    async def workflow_monitor_loop(self):
        """Monitor workflow progress and handle failures"""
        while self.running:
            try:
                # Check for stalled workflows
                # This is a simplified implementation
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Workflow monitor failed: {e}")
                await asyncio.sleep(60)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            'orchestrator_status': 'running' if self.running else 'stopped',
            'total_agents': len(self.agents),
            'agent_status': self.agent_status.copy(),
            'redis_connected': bool(self.redis_client),
            'workflows_defined': len(self.workflows),
            'active_tasks': len(self.tasks)
        }
        
        # Add queue statistics
        if self.redis_client:
            try:
                queue_stats = {}
                for agent_name in self.agents:
                    queue_name = f"agent_{agent_name}_queue"
                    queue_length = await self.redis_client.llen(queue_name)
                    queue_stats[agent_name] = {
                        'queue_length': queue_length,
                        'total_processed': await self.redis_client.get(f"stats:queue:{queue_name}:total") or 0
                    }
                status['queue_stats'] = queue_stats
                
            except Exception as e:
                logger.error(f"Error getting queue stats: {e}")
                
        return status
    
    async def clear_all_queues(self):
        """Clear all agent queues (useful for development/testing)"""
        if not self.redis_client:
            return
            
        try:
            for agent_name in self.agents:
                queue_name = f"agent_{agent_name}_queue"
                cleared_count = await self.redis_client.delete(queue_name)
                if cleared_count:
                    logger.info(f"Cleared {cleared_count} items from {queue_name}")
                    
        except Exception as e:
            logger.error(f"Error clearing queues: {e}")
    
    @asynccontextmanager
    async def lifespan_context(self):
        """Context manager for orchestrator lifecycle"""
        try:
            await self.start()
            yield self
        finally:
            await self.shutdown()