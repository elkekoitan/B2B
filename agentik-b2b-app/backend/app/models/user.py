from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
from uuid import UUID

# Base model with common fields
class BaseTimestamp(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# Company models
class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = Field(None, max_length=100)
    tax_number: Optional[str] = Field(None, max_length=50)
    contact_person: Optional[str] = Field(None, max_length=255)

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = Field(None, max_length=100)
    tax_number: Optional[str] = Field(None, max_length=50)
    contact_person: Optional[str] = Field(None, max_length=255)

class Company(CompanyBase, BaseTimestamp):
    id: UUID
    
    class Config:
        from_attributes = True

# User models
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    BUYER = "buyer"
    SUPPLIER = "supplier"

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=255)
    role: UserRole = UserRole.USER
    phone: Optional[str] = Field(None, max_length=50)
    is_active: bool = True

class UserCreate(UserBase):
    auth_user_id: UUID
    company_id: UUID

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)
    role: Optional[UserRole] = None
    phone: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None

class User(UserBase, BaseTimestamp):
    id: UUID
    auth_user_id: UUID
    company_id: UUID
    company: Optional[Company] = None
    
    class Config:
        from_attributes = True