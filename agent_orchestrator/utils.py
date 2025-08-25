import redis
import os
from typing import Optional
from loguru import logger

def get_redis_connection() -> redis.Redis:
    """Get Redis connection with proper configuration"""
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        client = redis.from_url(redis_url, decode_responses=True)
        
        # Test connection
        client.ping()
        logger.info(f"Connected to Redis at {redis_url}")
        
        return client
        
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount"""
    if currency == "USD":
        return f"${amount:,.2f}"
    return f"{amount:,.2f} {currency}"

def calculate_days_difference(start_date: str, end_date: str) -> int:
    """Calculate difference in days between two ISO format dates"""
    from datetime import datetime
    
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        return (end - start).days
    except ValueError as e:
        logger.error(f"Date parsing error: {e}")
        return 0

def sanitize_email(email: str) -> str:
    """Basic email sanitization"""
    return email.strip().lower()

def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def extract_keywords(text: str, min_length: int = 3) -> list:
    """Extract keywords from text"""
    import re
    
    # Remove special characters and split into words
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    # Filter by minimum length and remove common stop words
    stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
    keywords = [word for word in words if len(word) >= min_length and word not in stop_words]
    
    # Remove duplicates while preserving order
    unique_keywords = []
    for keyword in keywords:
        if keyword not in unique_keywords:
            unique_keywords.append(keyword)
    
    return unique_keywords[:10]  # Return top 10 keywords

def generate_reference_number(prefix: str = "REF") -> str:
    """Generate a unique reference number"""
    import uuid
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d")
    unique_id = str(uuid.uuid4())[:8].upper()
    
    return f"{prefix}-{timestamp}-{unique_id}"

def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """Safe division with default value for division by zero"""
    try:
        return a / b if b != 0 else default
    except (TypeError, ZeroDivisionError):
        return default

def percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100

def get_file_size_mb(file_size_bytes: int) -> float:
    """Convert file size from bytes to MB"""
    return file_size_bytes / (1024 * 1024)

def is_business_day(date_str: str) -> bool:
    """Check if given date is a business day (Monday-Friday)"""
    from datetime import datetime
    
    try:
        date_obj = datetime.fromisoformat(date_str)
        return date_obj.weekday() < 5  # 0-4 are Monday-Friday
    except ValueError:
        return False

def calculate_business_days(start_date: str, end_date: str) -> int:
    """Calculate number of business days between two dates"""
    from datetime import datetime, timedelta
    
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        # Ensure start is before end
        if start > end:
            start, end = end, start
        
        business_days = 0
        current_date = start
        
        while current_date <= end:
            if current_date.weekday() < 5:  # Monday = 0, Sunday = 6
                business_days += 1
            current_date += timedelta(days=1)
        
        return business_days
        
    except ValueError as e:
        logger.error(f"Date parsing error in calculate_business_days: {e}")
        return 0