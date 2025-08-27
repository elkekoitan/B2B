from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List
from uuid import UUID

from app.core.auth import get_current_user_profile
from app.core.database import get_db
from app.core.permissions import require_permission
from app.models.email import Notification, NotificationCreate, NotificationType
from app.models.common import APIResponse, PaginatedResponse, FilterParams
from supabase import Client
from loguru import logger

router = APIRouter()


@router.get("", response_model=APIResponse[PaginatedResponse[Notification]])
async def get_notifications(
    params: FilterParams = Depends(),
    notification_type: Optional[NotificationType] = None,
    read: Optional[bool] = None,
    current_user = Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("notifications:read")),
):
    try:
        query = db.table("notifications").select("*").eq("user_id", current_user["id"])
        if notification_type:
            query = query.eq("type", notification_type.value)
        if read is not None:
            query = query.eq("read", read)
        if params.search:
            query = query.or_(f"title.ilike.%{params.search}%,message.ilike.%{params.search}%")
        offset = (params.page - 1) * params.size
        query = query.range(offset, offset + params.size - 1)
        if params.sort_by:
            ascending = params.sort_order == "asc"
            query = query.order(params.sort_by, desc=not ascending)
        else:
            query = query.order("created_at", desc=True)
        result = query.execute()
        count_query = db.table("notifications").select("id", count="exact").eq("user_id", current_user["id"])
        if notification_type:
            count_query = count_query.eq("type", notification_type.value)
        if read is not None:
            count_query = count_query.eq("read", read)
        count_result = count_query.execute()
        total = count_result.count or 0
        has_next = (params.page * params.size) < total
        has_previous = params.page > 1
        paginated_data = PaginatedResponse(
            data=result.data or [],
            total=total,
            page=params.page,
            size=params.size,
            has_next=has_next,
            has_previous=has_previous,
        )
        return APIResponse(success=True, data=paginated_data)
    except Exception as e:
        logger.error(f"Notifications error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Bildirimler alınırken hata oluştu")


@router.get("/unread-count", response_model=APIResponse[dict])
async def get_unread_count(
    current_user = Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("notifications:read")),
):
    try:
        result = db.table("notifications").select("id", count="exact").eq("user_id", current_user["id"]).eq("read", False).execute()
        unread_count = result.count or 0
        return APIResponse(success=True, data={"unread_count": unread_count})
    except Exception as e:
        logger.error(f"Unread count error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Okunmamış bildirim sayısı alınırken hata oluştu")


@router.put("/{notification_id}/read", response_model=APIResponse[Notification])
async def mark_notification_as_read(
    notification_id: UUID,
    current_user = Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("notifications:read")),
):
    try:
        notification_check = db.table("notifications").select("user_id", "read").eq("id", str(notification_id)).single().execute()
        if not notification_check.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bildirim bulunamadı")
        if notification_check.data["user_id"] != current_user["id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu bildirimi görüntüleme yetkiniz yok")
        if notification_check.data["read"]:
            notification = db.table("notifications").select("*").eq("id", str(notification_id)).single().execute()
            return APIResponse(success=True, data=notification.data, message="Bildirim zaten okunmuş")
        result = db.table("notifications").update({"read": True, "updated_at": "now()"}).eq("id", str(notification_id)).execute()
        if not result.data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bildirim güncellenemedi")
        updated_notification = db.table("notifications").select("*").eq("id", str(notification_id)).single().execute()
        return APIResponse(success=True, data=updated_notification.data, message="Bildirim okundu olarak işaretlendi")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mark notification as read error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Bildirim güncellenirken hata oluştu")


@router.put("/mark-all-read", response_model=APIResponse[dict])
async def mark_all_notifications_as_read(
    current_user = Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("notifications:read")),
):
    try:
        result = db.table("notifications").update({"read": True, "updated_at": "now()"}).eq("user_id", current_user["id"]).eq("read", False).execute()
        updated_count = len(result.data) if result.data else 0
        return APIResponse(success=True, data={"updated_count": updated_count}, message=f"{updated_count} bildirim okundu olarak işaretlendi")
    except Exception as e:
        logger.error(f"Mark all notifications as read error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Bildirimler güncellenirken hata oluştu")


@router.delete("/{notification_id}", response_model=APIResponse[dict])
async def delete_notification(
    notification_id: UUID,
    current_user = Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("notifications:read")),
):
    try:
        notification_check = db.table("notifications").select("user_id").eq("id", str(notification_id)).single().execute()
        if not notification_check.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bildirim bulunamadı")
        if notification_check.data["user_id"] != current_user["id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu bildirimi silme yetkiniz yok")
        db.table("notifications").delete().eq("id", str(notification_id)).execute()
        return APIResponse(success=True, data={"id": str(notification_id)}, message="Bildirim başarıyla silindi")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete notification error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Bildirim silinirken hata oluştu")


@router.post("", response_model=APIResponse[Notification])
async def create_notification(
    notification_data: NotificationCreate,
    current_user = Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("notifications:write")),
):
    try:
        result = db.table("notifications").insert(notification_data.dict()).execute()
        if not result.data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bildirim oluşturulamadı")
        return APIResponse(success=True, data=result.data[0])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create notification error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Bildirim oluşturulurken hata oluştu")

