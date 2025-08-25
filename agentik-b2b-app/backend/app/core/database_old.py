from supabase import create_client, Client
from app.core.config import settings
from loguru import logger

# Global Supabase client
supabase: Client = None

async def init_db():
    """Initialize Supabase connection"""
    global supabase
    try:
        supabase = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY
        )
        logger.info("Supabase connection initialized successfully")
        return supabase
    except Exception as e:
        logger.error(f"Failed to initialize Supabase connection: {e}")
        raise

def get_db() -> Client:
    """Get Supabase client dependency"""
    return supabase

async def test_connection():
    """Test database connection"""
    try:
        result = supabase.table("companies").select("id").limit(1).execute()
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False