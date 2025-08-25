from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID

from .user import BaseTimestamp

# Email models
class EmailType(str, Enum):
    RFQ_INVITATION = "rfq_invitation"
    OFFER_SUBMISSION = "offer_submission"
    OFFER_UPDATE = "offer_update"
    RFQ_AWARD = "rfq_award"
    GENERAL_NOTIFICATION = "general_notification"
    WELCOME = "welcome"
    PASSWORD_RESET = "password_reset"

class EmailStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    FAILED = "failed"
    BOUNCED = "bounced"

class EmailBase(BaseModel):
    sender_email: EmailStr
    recipient_email: EmailStr
    subject: str = Field(..., max_length=500)
    body: str
    email_type: EmailType

class EmailCreate(EmailBase):
    rfq_id: Optional[UUID] = None
    offer_id: Optional[UUID] = None

class EmailLog(EmailBase, BaseTimestamp):
    id: UUID
    rfq_id: Optional[UUID] = None
    offer_id: Optional[UUID] = None
    status: EmailStatus
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True

# Notification models
class NotificationType(str, Enum):
    NEW_RFQ = "new_rfq"
    NEW_OFFER = "new_offer"
    OFFER_UPDATE = "offer_update"
    RFQ_DEADLINE = "rfq_deadline"
    RFQ_AWARD = "rfq_award"
    SYSTEM = "system"
    WARNING = "warning"
    INFO = "info"

class NotificationBase(BaseModel):
    type: NotificationType
    title: str = Field(..., max_length=255)
    message: str
    data: Optional[Dict[str, Any]] = None

class NotificationCreate(NotificationBase):
    user_id: UUID

class Notification(NotificationBase):
    id: UUID
    user_id: UUID
    read: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True

# Attachment models
class AttachmentBase(BaseModel):
    file_name: str = Field(..., max_length=255)
    file_path: str = Field(..., max_length=500)
    file_size: Optional[int] = None
    file_type: Optional[str] = Field(None, max_length=100)

class AttachmentCreate(AttachmentBase):
    rfq_id: Optional[UUID] = None
    offer_id: Optional[UUID] = None
    uploaded_by: UUID

class Attachment(AttachmentBase):
    id: UUID
    rfq_id: Optional[UUID] = None
    offer_id: Optional[UUID] = None
    uploaded_by: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True