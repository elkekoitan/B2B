from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
from uuid import UUID
from decimal import Decimal

from .user import BaseTimestamp, Company
from .rfq import RFQ

# Supplier models
class SupplierBase(BaseModel):
    specializations: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    profile_completion_score: int = Field(default=0, ge=0, le=100)

class SupplierCreate(SupplierBase):
    company_id: UUID

class SupplierUpdate(BaseModel):
    specializations: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    profile_completion_score: Optional[int] = Field(None, ge=0, le=100)

class Supplier(SupplierBase, BaseTimestamp):
    id: UUID
    company_id: UUID
    rating: Decimal = Field(default=0, ge=0, le=5)
    total_completed_orders: int = 0
    average_response_time: int = 0  # in hours
    verified: bool = False
    verification_date: Optional[datetime] = None
    company: Optional[Company] = None
    
    class Config:
        from_attributes = True

# Offer models
class OfferStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"

class OfferBase(BaseModel):
    price: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)
    delivery_time: Optional[int] = Field(None, gt=0)  # in days
    delivery_terms: Optional[str] = None
    warranty_terms: Optional[str] = None
    payment_terms: Optional[str] = None
    technical_specs: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    valid_until: Optional[date] = None
    
    @validator('valid_until')
    def validate_validity(cls, v):
        if v is not None and v < date.today():
            raise ValueError('Validity date must be in the future')
        return v

class OfferCreate(OfferBase):
    rfq_id: UUID
    supplier_id: UUID

class OfferUpdate(BaseModel):
    price: Optional[Decimal] = Field(None, gt=0)
    currency: Optional[str] = Field(None, max_length=3)
    delivery_time: Optional[int] = Field(None, gt=0)
    delivery_terms: Optional[str] = None
    warranty_terms: Optional[str] = None
    payment_terms: Optional[str] = None
    technical_specs: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    status: Optional[OfferStatus] = None
    valid_until: Optional[date] = None

class Offer(OfferBase, BaseTimestamp):
    id: UUID
    rfq_id: UUID
    supplier_id: UUID
    status: OfferStatus
    rfq: Optional[RFQ] = None
    supplier: Optional[Supplier] = None
    
    class Config:
        from_attributes = True