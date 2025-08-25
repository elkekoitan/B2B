from supabase import Client
from loguru import logger
from typing import Dict, Any, Optional
from uuid import UUID

class NotificationService:
    """Service for managing notifications"""
    
    @staticmethod
    async def create_notification(
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        db: Client = None
    ) -> Optional[Dict[str, Any]]:
        """Create a new notification for a user"""
        try:
            notification_data = {
                "user_id": user_id,
                "type": notification_type,
                "title": title,
                "message": message,
                "data": data or {},
                "read": False
            }
            
            result = db.table("notifications").insert(notification_data).execute()
            
            if result.data:
                logger.info(f"Notification created for user {user_id}: {title}")
                return result.data[0]
            else:
                logger.error(f"Failed to create notification for user {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return None
    
    @staticmethod
    async def create_bulk_notifications(
        notifications: list[Dict[str, Any]],
        db: Client
    ) -> bool:
        """Create multiple notifications in bulk"""
        try:
            result = db.table("notifications").insert(notifications).execute()
            
            if result.data:
                logger.info(f"Created {len(result.data)} notifications")
                return True
            else:
                logger.error("Failed to create bulk notifications")
                return False
                
        except Exception as e:
            logger.error(f"Error creating bulk notifications: {e}")
            return False
    
    @staticmethod
    async def mark_as_read(
        notification_id: str,
        user_id: str,
        db: Client
    ) -> bool:
        """Mark a notification as read"""
        try:
            result = db.table("notifications").update({
                "read": True
            }).eq("id", notification_id).eq("user_id", user_id).execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return False
    
    @staticmethod
    async def get_unread_count(user_id: str, db: Client) -> int:
        """Get count of unread notifications for a user"""
        try:
            result = db.table("notifications").select("id").eq(
                "user_id", user_id
            ).eq("read", False).execute()
            
            return len(result.data) if result.data else 0
            
        except Exception as e:
            logger.error(f"Error getting unread count: {e}")
            return 0