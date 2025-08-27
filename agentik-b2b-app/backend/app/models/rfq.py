from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
from uuid import UUID
from decimal import Decimal

from .user import BaseTimestamp, Company

# RFQ models
class RFQStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    IN_REVIEW = "in_review"
    AWARDED = "awarded"
    CANCELLED = "cancelled"
    CLOSED = "closed"

class RFQPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class RFQBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=10)
    category: Optional[str] = Field(None, max_length=100)
    quantity: Optional[int] = Field(None, gt=0)
    unit: Optional[str] = Field(None, max_length=50)
    currency: Optional[str] = Field("USD", max_length=3)
    budget_min: Optional[Decimal] = Field(None, ge=0)
    budget_max: Optional[Decimal] = Field(None, ge=0)
    deadline_date: Optional[date] = None
    delivery_location: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = None
    priority: RFQPriority = RFQPriority.MEDIUM
    attachments: Optional[List[Dict[str, Any]]] = None
    
    @validator('budget_max')
    def validate_budget_range(cls, v, values):
        if v is not None and 'budget_min' in values and values['budget_min'] is not None:
            if v < values['budget_min']:
                raise ValueError('Maximum budget must be greater than minimum budget')
        return v
    
    @validator('deadline_date')
    def validate_deadline(cls, v):
        if v is not None and v < date.today():
            raise ValueError('Deadline must be in the future')
        return v

class RFQCreate(RFQBase):
    pass

class RFQCreateWithTemplate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=10)
    category: str = Field(..., max_length=100)
    quantity: Optional[int] = Field(None, gt=0)
    unit: Optional[str] = Field(None, max_length=50)
    budget_min: Optional[Decimal] = Field(None, ge=0)
    budget_max: Optional[Decimal] = Field(None, ge=0)
    deadline_date: Optional[date] = None
    delivery_location: Optional[str] = None
    priority: RFQPriority = RFQPriority.MEDIUM
    attachments: Optional[List[Dict[str, Any]]] = None
    extra_fields: Dict[str, Any] = Field(default_factory=dict)

class RFQUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[str] = Field(None, max_length=100)
    quantity: Optional[int] = Field(None, gt=0)
    unit: Optional[str] = Field(None, max_length=50)
    currency: Optional[str] = Field(None, max_length=3)
    budget_min: Optional[Decimal] = Field(None, ge=0)
    budget_max: Optional[Decimal] = Field(None, ge=0)
    deadline_date: Optional[date] = None
    delivery_location: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = None
    status: Optional[RFQStatus] = None
    priority: Optional[RFQPriority] = None
    attachments: Optional[List[Dict[str, Any]]] = None

class RFQ(RFQBase, BaseTimestamp):
    id: UUID
    requester_id: UUID
    company_id: UUID
    status: RFQStatus
    company: Optional[Company] = None
    
    class Config:
        from_attributes = True

# RFQ with additional data for detailed views
class RFQDetail(RFQ):
    offer_count: int = 0
    average_offer_price: Optional[Decimal] = None
    lowest_offer_price: Optional[Decimal] = None
    highest_offer_price: Optional[Decimal] = None
