import asyncio
import os
from loguru import logger
from orchestrator import AgentOrchestrator

# Configure logging
logger.add("/app/logs/main.log", rotation="1 day", retention="7 days", level="INFO")

async def main():
    """Main entry point for the agent orchestrator system"""
    logger.info("Starting Agentik Agent Orchestrator System")
    
    # Create orchestrator instance
    orchestrator = AgentOrchestrator()
    
    # Perform health check
    health = await orchestrator.health_check()
    logger.info(f"Health check: {health}")
    
    if not health["redis"]["connected"]:
        logger.error("Redis connection failed. Exiting.")
        return
    
    try:
        # Start the orchestrator
        logger.info("Agent Orchestrator is starting...")
        await orchestrator.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal. Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logger.info("Agent Orchestrator stopped.")

if __name__ == "__main__":
    # Set up environment
    os.makedirs("/app/logs", exist_ok=True)
    
    # Log startup info
    logger.info("=" * 50)
    logger.info("Agentik B2B Agent Orchestrator")
    logger.info("=" * 50)
    logger.info(f"Python version: {os.sys.version}")
    logger.info(f"Environment variables loaded:")
    logger.info(f"  - REDIS_URL: {os.getenv('REDIS_URL', 'Not set')}")
    logger.info(f"  - SUPABASE_URL: {os.getenv('SUPABASE_URL', 'Not set')}")
    logger.info(f"  - EMAIL_USERNAME: {'Set' if os.getenv('EMAIL_USERNAME') else 'Not set'}")
    logger.info("=" * 50)
    
    # Run the main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application terminated by user.")
    except Exception as e:
        logger.error(f"Application crashed: {e}")
        raise