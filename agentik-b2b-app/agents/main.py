#!/usr/bin/env python3

"""
Main entry point for the AI Agent System

This module initializes and runs all 6 AI agents:
1. RFQ Intake Agent - Processes and validates new RFQ submissions
2. Supplier Discovery Agent - Finds and matches suppliers to RFQs
3. Email Send Agent - Handles email communications
4. Inbox Parser Agent - Parses incoming email responses
5. Supplier Verifier Agent - Verifies supplier credibility and offers
6. Aggregation & Report Agent - Generates comprehensive reports
"""

import asyncio
import signal
import sys
import os
from pathlib import Path
from loguru import logger
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

# Import core components
from core.orchestrator import AgentOrchestrator
from core.redis_client import init_redis, close_redis
from core.database import init_db_pool, close_db_pool

# Import all agents
from agents.rfq_intake_agent import RFQIntakeAgent
from agents.supplier_discovery_agent import SupplierDiscoveryAgent
from agents.email_send_agent import EmailSendAgent
from agents.inbox_parser_agent import InboxParserAgent
from agents.supplier_verifier_agent import SupplierVerifierAgent
from agents.aggregation_report_agent import AggregationReportAgent

def setup_logging():
    """Setup comprehensive logging configuration"""
    # Remove default logger
    logger.remove()
    
    # Console logging with colors
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )
    
    # File logging for errors
    logger.add(
        "logs/agent_system_errors.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="10 MB",
        retention="7 days"
    )
    
    # File logging for all events
    logger.add(
        "logs/agent_system.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO",
        rotation="50 MB",
        retention="3 days"
    )
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

def setup_signal_handlers(orchestrator: AgentOrchestrator):
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}. Starting graceful shutdown...")
        asyncio.create_task(shutdown_system(orchestrator))
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

async def shutdown_system(orchestrator: AgentOrchestrator):
    """Gracefully shutdown the entire system"""
    logger.info("🛑 Initiating system shutdown...")
    
    try:
        # Shutdown orchestrator (this will shutdown all agents)
        await orchestrator.shutdown()
        
        # Close database connections
        await close_db_pool()
        
        # Close Redis connections
        await close_redis()
        
        logger.info("✅ System shutdown completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Error during system shutdown: {e}")
    finally:
        # Force exit
        os._exit(0)

async def initialize_system() -> AgentOrchestrator:
    """Initialize all system components"""
    logger.info("🚀 Initializing AI Agent System...")
    
    # Initialize Redis connection
    logger.info("🔗 Connecting to Redis...")
    try:
        await init_redis()
        logger.info("✅ Redis connection established")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        raise
    
    # Initialize database connection pool
    logger.info("🗄️  Initializing database connection pool...")
    try:
        await init_db_pool()
        logger.info("✅ Database connection pool initialized")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise
    
    # Create orchestrator
    orchestrator = AgentOrchestrator()
    
    # Initialize and register all agents
    logger.info("🤖 Initializing AI Agents...")
    
    agents = [
        RFQIntakeAgent(),
        SupplierDiscoveryAgent(),
        EmailSendAgent(),
        InboxParserAgent(),
        SupplierVerifierAgent(),
        AggregationReportAgent()
    ]
    
    for agent in agents:
        logger.info(f"   📝 Registering {agent.name}")
        await orchestrator.register_agent(agent)
    
    logger.info(f"✅ Registered {len(agents)} agents successfully")
    
    return orchestrator

async def run_system_diagnostics(orchestrator: AgentOrchestrator):
    """Run system diagnostics and health checks"""
    logger.info("🔍 Running system diagnostics...")
    
    try:
        # Get system status
        status = await orchestrator.get_system_status()
        
        logger.info(f"📊 System Status:")
        logger.info(f"   - Orchestrator: {status['orchestrator_status']}")
        logger.info(f"   - Total Agents: {status['total_agents']}")
        logger.info(f"   - Redis Connected: {status['redis_connected']}")
        logger.info(f"   - Active Tasks: {status['active_tasks']}")
        
        # Check agent status
        for agent_name, agent_status in status['agent_status'].items():
            health = agent_status.get('health', 'unknown')
            processed = agent_status.get('tasks_processed', 0)
            failed = agent_status.get('tasks_failed', 0)
            success_rate = (processed / max(1, processed + failed)) * 100
            
            logger.info(f"   - {agent_name}: {health} (Success rate: {success_rate:.1f}%)")
        
        logger.info("✅ System diagnostics completed")
        
    except Exception as e:
        logger.error(f"❌ System diagnostics failed: {e}")

async def simulate_rfq_workflow(orchestrator: AgentOrchestrator):
    """Simulate a complete RFQ workflow for testing"""
    logger.info("🧪 Starting RFQ workflow simulation...")
    
    try:
        # Simulate new RFQ data
        rfq_data = {
            'action': 'process_rfq',
            'rfq_data': {
                'id': 'test_rfq_001',
                'title': 'Test RFQ - Elektronik Komponentler',
                'description': 'Test amaçlı elektronik komponent alımı',
                'category': 'elektronik',
                'budget_min': 1000,
                'budget_max': 5000,
                'priority': 'medium',
                'status': 'published'
            }
        }
        
        # Start RFQ processing workflow
        success = await orchestrator.execute_workflow('rfq_processing', rfq_data)
        
        if success:
            logger.info("✅ RFQ workflow simulation started successfully")
        else:
            logger.error("❌ Failed to start RFQ workflow simulation")
            
    except Exception as e:
        logger.error(f"❌ RFQ workflow simulation failed: {e}")

async def start_periodic_tasks(orchestrator: AgentOrchestrator):
    """Start periodic maintenance tasks"""
    async def daily_report_task():
        while True:
            try:
                # Wait for next day (simplified - runs every 24 hours)
                await asyncio.sleep(24 * 60 * 60)
                
                logger.info("📊 Generating daily report...")
                
                # Queue daily report task
                await orchestrator.queue_task('aggregation_report_agent', {
                    'action': 'generate_daily_report',
                    'date': datetime.now().date().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Error in daily report task: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying
    
    # Start daily report task
    asyncio.create_task(daily_report_task())
    logger.info("⏰ Periodic tasks started")

async def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()
    
    logger.info("🌟 Starting Agentik B2B AI Agent System")
    logger.info("🎯 Full implementation with 6 AI agents")
    logger.info("📅 Started at: {}", datetime.now().isoformat())
    
    orchestrator = None
    
    try:
        # Initialize system
        orchestrator = await initialize_system()
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(orchestrator)
        
        # Start the orchestrator
        logger.info("🎮 Starting orchestrator...")
        await orchestrator.start()
        
        # Run system diagnostics
        await run_system_diagnostics(orchestrator)
        
        # Start periodic tasks
        await start_periodic_tasks(orchestrator)
        
        # Optional: Simulate workflow for testing
        # Uncomment the line below to run a test workflow
        # await simulate_rfq_workflow(orchestrator)
        
        logger.info("🎉 AI Agent System is now running!")
        logger.info("💡 System ready to process RFQs and manage supplier workflows")
        logger.info("🛑 Press Ctrl+C to stop the system")
        
        # Keep the system running
        while orchestrator.running:
            await asyncio.sleep(10)
            
            # Periodic health check log
            status = await orchestrator.get_system_status()
            healthy_agents = sum(1 for agent_status in status['agent_status'].values() 
                               if agent_status.get('health') == 'healthy')
            
            logger.info(f"💓 System heartbeat: {healthy_agents}/{status['total_agents']} agents healthy")
        
    except KeyboardInterrupt:
        logger.info("🛑 Received shutdown signal")
    except Exception as e:
        logger.error(f"❌ Critical system error: {e}")
        raise
    finally:
        if orchestrator:
            await shutdown_system(orchestrator)

if __name__ == "__main__":
    try:
        # Run the main application
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Goodbye! System stopped by user")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)