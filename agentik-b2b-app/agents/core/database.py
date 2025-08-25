import asyncpg
import os
from loguru import logger
from typing import Optional
from contextlib import asynccontextmanager

# Global database pool
db_pool: Optional[asyncpg.Pool] = None

async def init_db_pool():
    """Initialize database connection pool"""
    global db_pool
    
    try:
        # Get database configuration from environment
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            # Build connection string from individual components
            host = os.getenv('DB_HOST', 'localhost')
            port = os.getenv('DB_PORT', '5432')
            database = os.getenv('DB_NAME', 'agentik_db')
            user = os.getenv('DB_USER', 'postgres')
            password = os.getenv('DB_PASS', 'password')
            
            database_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        # Create connection pool
        db_pool = await asyncpg.create_pool(
            database_url,
            min_size=5,
            max_size=20,
            command_timeout=30,
            server_settings={
                'application_name': 'agentik_agent_system'
            }
        )
        
        # Test connection
        async with db_pool.acquire() as connection:
            await connection.execute('SELECT 1')
        
        logger.info("Database connection pool initialized successfully")
        return db_pool
        
    except Exception as e:
        logger.error(f"Failed to initialize database connection pool: {e}")
        raise

def get_db_pool() -> Optional[asyncpg.Pool]:
    """Get database connection pool"""
    return db_pool

async def close_db_pool():
    """Close database connection pool"""
    global db_pool
    if db_pool:
        await db_pool.close()
        db_pool = None
        logger.info("Database connection pool closed")

@asynccontextmanager
async def get_db_connection():
    """Get database connection from pool"""
    if not db_pool:
        raise RuntimeError("Database pool not initialized")
    
    async with db_pool.acquire() as connection:
        yield connection

async def test_db_connection() -> bool:
    """Test database connection"""
    if not db_pool:
        return False
    
    try:
        async with db_pool.acquire() as connection:
            result = await connection.fetchval('SELECT 1')
            return result == 1
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False

async def execute_query(query: str, *args):
    """Execute a database query"""
    if not db_pool:
        raise RuntimeError("Database pool not initialized")
    
    async with db_pool.acquire() as connection:
        return await connection.execute(query, *args)

async def fetch_one(query: str, *args):
    """Fetch single row from database"""
    if not db_pool:
        raise RuntimeError("Database pool not initialized")
    
    async with db_pool.acquire() as connection:
        return await connection.fetchrow(query, *args)

async def fetch_many(query: str, *args):
    """Fetch multiple rows from database"""
    if not db_pool:
        raise RuntimeError("Database pool not initialized")
    
    async with db_pool.acquire() as connection:
        return await connection.fetch(query, *args)

async def fetch_value(query: str, *args):
    """Fetch single value from database"""
    if not db_pool:
        raise RuntimeError("Database pool not initialized")
    
    async with db_pool.acquire() as connection:
        return await connection.fetchval(query, *args)