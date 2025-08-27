from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Enums
class RFQStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class OfferStatus(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class JobStatus(str, Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class UserRole(str, Enum):
    ADMIN = "admin"
    BUYER = "buyer"
    SUPPLIER = "supplier"
    MANAGER = "manager"
    USER = "user"

# Base Models
class BaseResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None

# User Models
class User(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = "user"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UserRoleModel(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    permissions: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class RoleAssignment(BaseModel):
    id: str
    user_id: str
    role_id: str
    assigned_by: Optional[str] = None
    assigned_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = True

# RFQ Models
class RFQCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=500)
    description: str = Field(..., min_length=10, max_length=10000)
    category: str = Field(..., min_length=2, max_length=100)
    quantity: int = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=50)
    budget_min: Optional[float] = Field(None, ge=0)
    budget_max: Optional[float] = Field(None, ge=0)
    deadline: datetime
    delivery_location: str = Field(..., min_length=3, max_length=1000)
    requirements: Optional[str] = Field(None, max_length=5000)
    priority: Optional[str] = Field('medium', pattern='^(low|medium|high)$')
    
    @validator('budget_max')
    def budget_max_greater_than_min(cls, v, values):
        if 'budget_min' in values and values['budget_min'] and v:
            if v <= values['budget_min']:
                raise ValueError('Maximum budget must be greater than minimum budget')
        return v
    
    @validator('deadline')
    def deadline_future(cls, v):
        from datetime import timezone
        now = datetime.now(timezone.utc) if v.tzinfo else datetime.now()
        if v <= now:
            raise ValueError('Deadline must be in the future')
        return v

class RFQUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    category: Optional[str] = Field(None, min_length=2, max_length=100)
    quantity: Optional[int] = Field(None, gt=0)
    unit: Optional[str] = Field(None, min_length=1, max_length=50)
    budget_min: Optional[float] = Field(None, ge=0)
    budget_max: Optional[float] = Field(None, ge=0)
    deadline: Optional[datetime] = None
    delivery_location: Optional[str] = Field(None, min_length=3, max_length=200)
    requirements: Optional[str] = Field(None, max_length=1000)
    status: Optional[RFQStatus] = None

class RFQ(BaseModel):
    id: str
    title: str
    description: str
    category: Optional[str] = None
    quantity: Optional[int] = None
    unit: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    deadline_date: Optional[datetime] = None
    delivery_location: Optional[str] = None
    requirements: Optional[Union[str, Dict[str, Any]]] = None
    status: RFQStatus = RFQStatus.DRAFT
    priority: Optional[str] = 'medium'
    requester_id: str
    company_id: Optional[str] = None
    attachments: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

# Supplier Models
class SupplierCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str
    phone: Optional[str] = Field(None, max_length=20)
    company: str = Field(..., min_length=2, max_length=100)
    address: Optional[str] = Field(None, max_length=300)
    website: Optional[str] = Field(None, max_length=200)
    categories: List[str] = Field(..., min_items=1)
    description: Optional[str] = Field(None, max_length=500)

class Supplier(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str]
    company: str
    address: Optional[str]
    website: Optional[str]
    categories: List[str]
    description: Optional[str]
    verified: bool = False
    rating: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime]

# Offer Models
class OfferCreate(BaseModel):
    rfq_id: str
    supplier_id: str
    unit_price: float = Field(..., gt=0)
    total_price: float = Field(..., gt=0)
    delivery_time: int = Field(..., gt=0)  # days
    terms: Optional[str] = Field(None, max_length=1000)
    notes: Optional[str] = Field(None, max_length=500)
    
    @validator('total_price')
    def total_price_consistent(cls, v, values):
        if 'unit_price' in values and 'quantity' in values:
            expected = values['unit_price'] * values.get('quantity', 1)
            if abs(v - expected) > 0.01:  # Allow small floating point differences
                raise ValueError('Total price must equal unit price × quantity')
        return v

class Offer(BaseModel):
    id: str
    rfq_id: str
    supplier_id: str
    unit_price: float
    total_price: float
    delivery_time: int
    terms: Optional[str]
    notes: Optional[str]
    status: OfferStatus
    submitted_at: datetime
    updated_at: Optional[datetime]

# Email Models
class EmailLog(BaseModel):
    id: str
    rfq_id: str
    supplier_id: str
    email_type: str  # "invitation", "reminder", "notification"
    recipient: str
    subject: str
    body: str
    sent_at: datetime
    delivery_status: str  # "sent", "delivered", "failed"
    error_message: Optional[str]

# Job/Agent Models
class JobCreate(BaseModel):
    job_type: str = Field(..., pattern="^(rfq_process|supplier_discovery|email_campaign)$")
    rfq_id: str
    payload: Dict[str, Any] = {}

class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    created_at: datetime
    updated_at: Optional[datetime]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Response Models
class RFQListResponse(BaseResponse):
    data: Optional[List[RFQ]] = None
    total: Optional[int] = None
    page: Optional[int] = None
    per_page: Optional[int] = None

class SupplierListResponse(BaseResponse):
    data: Optional[List[Supplier]] = None
    total: Optional[int] = None

class OfferListResponse(BaseResponse):
    data: Optional[List[Offer]] = None
    total: Optional[int] = None

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, Dict[str, Any]]

# Analytics Models
class RFQAnalytics(BaseModel):
    total_rfqs: int
    active_rfqs: int
    completed_rfqs: int
    avg_response_time: Optional[float]  # hours
    avg_offers_per_rfq: Optional[float]
    top_categories: List[Dict[str, Any]]

class OfferComparison(BaseModel):
    rfq_id: str
    offers: List[Offer]
    analysis: Dict[str, Any]
    recommendations: List[str]

# Catalog Models
class CatalogCreate(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    price: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field('USD', min_length=3, max_length=3)
    supplier_id: Optional[str] = None

class CatalogUpdate(BaseModel):
    product_name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    price: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)

class CatalogItem(BaseModel):
    id: str
    supplier_id: str
    product_name: str
    category: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = 'USD'
    created_at: datetime
    updated_at: Optional[datetime] = None

class CatalogListResponse(BaseResponse):
    data: Optional[List[CatalogItem]] = None
    total: Optional[int] = None
