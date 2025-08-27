from supabase import create_client, Client
from app.core.config import settings
from loguru import logger
from typing import Optional

# Global Supabase clients
supabase: Optional[Client] = None
supabase_admin: Optional[Client] = None


async def init_db():
    """Initialize Supabase connections"""
    global supabase, supabase_admin
    try:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
        if settings.SUPABASE_SERVICE_ROLE_KEY:
            supabase_admin = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
            logger.info("Supabase admin connection initialized")
        logger.info("Supabase connection initialized successfully")
        return supabase
    except Exception as e:
        logger.error(f"Failed to initialize Supabase connection: {e}")
        raise


def get_db() -> Client:
    """Get Supabase client dependency"""
    if not supabase:
        raise RuntimeError("Database not initialized")
    return supabase


def get_admin_db() -> Client:
    """Get Supabase admin client (with service role key)"""
    if not supabase_admin:
        return get_db()
    return supabase_admin


async def test_connection():
    """Test database connection"""
    try:
        if not supabase:
            return False
        supabase.table("companies").select("id").limit(1).execute()
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


async def execute_rpc(function_name: str, params: dict = None):
    """Execute a database RPC function"""
    try:
        if not supabase:
            raise RuntimeError("Database not initialized")
        result = supabase.rpc(function_name, params or {}).execute()
        return result
    except Exception as e:
        logger.error(f"RPC execution failed: {function_name} - {e}")
        raise

