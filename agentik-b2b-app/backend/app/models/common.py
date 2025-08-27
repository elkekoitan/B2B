from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Generic, TypeVar
from datetime import datetime
from enum import Enum
from uuid import UUID

# Generic response types
T = TypeVar('T')

class BaseTimestamp(BaseModel):
    """Base model with timestamp fields"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class APIResponse(BaseModel, Generic[T]):
    """Generic API response wrapper"""
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
    error: Optional[str] = None

class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper"""
    data: List[T]
    total: int
    page: int
    size: int
    has_next: bool
    has_previous: bool

class FilterParams(BaseModel):
    """Base filter parameters"""
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
    sort_by: Optional[str] = None
    sort_order: Optional[str] = Field(default="asc", pattern=r"^(asc|desc)$")
    search: Optional[str] = None

# Job status enum
class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Job model
class JobCreate(BaseModel):
    job_type: str
    data: Dict[str, Any]
    priority: int = 1

class Job(BaseModel):
    id: str
    job_type: str
    status: JobStatus
    data: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    priority: int = 1
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

# Error models
class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None

# Notification models
class NotificationType(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"

class NotificationBase(BaseModel):
    title: str
    message: str
    type: NotificationType = NotificationType.INFO
    read: bool = False
    metadata: Optional[Dict[str, Any]] = None

class NotificationCreate(NotificationBase):
    user_id: UUID

class Notification(NotificationBase, BaseTimestamp):
    id: UUID
    user_id: UUID
    
    class Config:
        from_attributes = True
