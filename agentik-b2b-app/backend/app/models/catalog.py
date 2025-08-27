from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal
from .user import BaseTimestamp


class CatalogItemBase(BaseModel):
    product_name: str = Field(..., max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    price: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field("USD", max_length=3)
    moq: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None


class CatalogItemCreate(CatalogItemBase):
    supplier_id: UUID


class CatalogItemUpdate(BaseModel):
    product_name: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    price: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    moq: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None


class CatalogItem(CatalogItemBase, BaseTimestamp):
    id: UUID
    supplier_id: UUID

    class Config:
        from_attributes = True

