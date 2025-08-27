import asyncio
import json
import os
from typing import Dict, Any, List
from loguru import logger
from datetime import datetime
from agents import (
    RFQIntakeAgent,
    SupplierDiscoveryAgent,
    EmailSendAgent,
    InboxParserAgent,
    SupplierVerifierAgent,
    AggregationReportAgent
)
from utils import get_redis_connection

class AgentOrchestrator:
    """Orchestrates the entire agent workflow"""
    
    def __init__(self):
        self.redis_client = get_redis_connection()
        self.agents = {
            "rfq_intake": RFQIntakeAgent(),
            "supplier_discovery": SupplierDiscoveryAgent(),
            "email_send": EmailSendAgent(),
            "inbox_parser": InboxParserAgent(),
            "supplier_verifier": SupplierVerifierAgent(),
            "aggregation_report": AggregationReportAgent()
        }
        self.running = False
        self._hb_task = None
        self._hb_key = "agentik:heartbeat"
        self._version = "1.0.0"
        
        # Workflow definition
        self.workflow = {
            "rfq_intake": "supplier_discovery",
            "supplier_discovery": "email_send",
            "email_send": "inbox_parser",
            "inbox_parser": "supplier_verifier",
            "supplier_verifier": "aggregation_report",
            "aggregation_report": None  # End of workflow
        }
    
    async def start(self):
        """Start the orchestrator and all agent workers"""
        self.running = True
        logger.info("Starting Agent Orchestrator...")
        
        # Start main job processor
        job_processor = asyncio.create_task(self._process_main_jobs())
        
        # Start individual agent workers
        agent_workers = []
        for agent_name, agent in self.agents.items():
            worker = asyncio.create_task(self._run_agent_worker(agent_name, agent))
            agent_workers.append(worker)
        # Start heartbeat
        self._hb_task = asyncio.create_task(self._heartbeat_loop())
        
        try:
            # Wait for all tasks to complete (they run indefinitely)
            await asyncio.gather(job_processor, *agent_workers)
        except KeyboardInterrupt:
            logger.info("Shutting down Agent Orchestrator...")
            self.running = False
            
            # Cancel all tasks
            job_processor.cancel()
            for worker in agent_workers:
                worker.cancel()
            if self._hb_task:
                self._hb_task.cancel()

    async def _process_main_jobs(self):
        """Process main job queue and route to first agent"""
        logger.info("Started main job processor")
        
        while self.running:
            try:
                # Get job from main queue
                result = self.redis_client.brpop("agentik:jobs", timeout=5)
                
                if result:
                    _, job_data_str = result
                    job_data = json.loads(job_data_str)
                    
                    logger.info(f"Processing new job: {job_data.get('job_id')}")
                    
                    # Route to first agent (RFQ Intake)
                    await self._route_to_agent("rfq_intake", job_data)
                    
            except Exception as e:
                logger.error(f"Error in main job processor: {e}")
                await asyncio.sleep(1)
    
    async def _run_agent_worker(self, agent_name: str, agent):
        """Run individual agent worker"""
        queue_name = f"agentik:agent:{agent_name}"
        logger.info(f"Started {agent_name} worker on queue {queue_name}")
        
        while self.running:
            try:
                # Get job from agent queue
                result = self.redis_client.brpop(queue_name, timeout=5)
                
                if result:
                    _, job_data_str = result
                    job_data = json.loads(job_data_str)
                    
                    job_id = job_data.get("job_id")
                    logger.info(f"[{agent_name}] Processing job {job_id}")
                    
                    # Update job status to in_progress
                    self._update_job_status(job_id, "in_progress", {
                        "current_agent": agent_name,
                        "started_at": datetime.utcnow().isoformat()
                    })
                    
                    # Process job with agent
                    result = await agent.process(job_data)
                    
                    if result.get("success"):
                        logger.info(f"[{agent_name}] Successfully processed job {job_id}")
                    else:
                        logger.error(f"[{agent_name}] Failed to process job {job_id}: {result.get('error')}")
                    
            except Exception as e:
                logger.error(f"Error in {agent_name} worker: {e}")
                await asyncio.sleep(1)
    
    async def _route_to_agent(self, agent_name: str, job_data: Dict[str, Any]):
        """Route job to specific agent"""
        queue_name = f"agentik:agent:{agent_name}"
        self.redis_client.lpush(queue_name, json.dumps(job_data))
        logger.info(f"Routed job {job_data.get('job_id')} to {agent_name}")
    
    def _update_job_status(self, job_id: str, status: str, result: Dict[str, Any] = None):
        """Update job status in Redis"""
        updates = {
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if result:
            updates["result"] = json.dumps(result)
        
        self.redis_client.hset(f"agentik:status:{job_id}", mapping=updates)
    
    async def process_job(self, job_data: Dict[str, Any]) -> str:
        """Process a single job through the workflow"""
        job_id = job_data.get("job_id")
        logger.info(f"Starting workflow for job {job_id}")
        
        # Store initial job status
        self._update_job_status(job_id, "queued", {
            "workflow_started": True,
            "total_agents": len(self.workflow)
        })
        
        # Add to main job queue
        self.redis_client.lpush("agentik:jobs", json.dumps(job_data))
        
        return job_id
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get current job status"""
        job_data = self.redis_client.hgetall(f"agentik:status:{job_id}")
        
        if not job_data:
            return None
        
        return {
            "job_id": job_id,
            "status": job_data.get("status", "unknown"),
            "created_at": job_data.get("created_at"),
            "updated_at": job_data.get("updated_at"),
            "result": json.loads(job_data.get("result", "null")),
            "error": job_data.get("error")
        }
    
    def get_workflow_stats(self) -> Dict[str, Any]:
        """Get workflow statistics"""
        stats = {
            "total_agents": len(self.agents),
            "agents": list(self.agents.keys()),
            "workflow": self.workflow,
            "running": self.running,
            "queue_sizes": {}
        }
        
        # Get queue sizes
        stats["queue_sizes"]["main_queue"] = self.redis_client.llen("agentik:jobs")
        
        for agent_name in self.agents.keys():
            queue_name = f"agentik:agent:{agent_name}"
            stats["queue_sizes"][agent_name] = self.redis_client.llen(queue_name)
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on orchestrator and agents"""
        health = {
            "orchestrator": {
                "running": self.running,
                "agents_count": len(self.agents),
                "timestamp": datetime.utcnow().isoformat()
            },
            "agents": {},
            "redis": {}
        }
        
        # Check Redis connection
        try:
            self.redis_client.ping()
            health["redis"] = {"status": "healthy", "connected": True}
        except Exception as e:
            health["redis"] = {"status": "unhealthy", "error": str(e), "connected": False}
        
        # Check individual agents (basic check)
        for agent_name, agent in self.agents.items():
            health["agents"][agent_name] = {
                "status": "healthy",  # In a real system, you might ping each agent
                "queue_size": self.redis_client.llen(f"agentik:agent:{agent_name}")
            }
        
        return health

    async def _heartbeat_loop(self):
        """Publish a lightweight heartbeat to Redis for observability."""
        try:
            while self.running:
                try:
                    snapshot = {
                        "ts": datetime.utcnow().isoformat(),
                        "running": self.running,
                        "version": self._version,
                        "agents": list(self.agents.keys()),
                        "queues": {
                            "main": self.redis_client.llen("agentik:jobs"),
                        },
                    }
                    for agent_name in self.agents.keys():
                        qn = f"agentik:agent:{agent_name}"
                        try:
                            snapshot["queues"][agent_name] = self.redis_client.llen(qn)
                        except Exception:
                            snapshot["queues"][agent_name] = None
                    # store as JSON string
                    self.redis_client.set(self._hb_key, json.dumps(snapshot))
                except Exception as e:
                    logger.warning(f"Heartbeat publish failed: {e}")
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            logger.info("Heartbeat loop cancelled")
            raise
