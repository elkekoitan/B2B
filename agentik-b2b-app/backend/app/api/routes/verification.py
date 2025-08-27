from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional

from app.core.auth import get_current_user_profile
from app.core.database import get_db
from app.core.permissions import require_permission
from app.models.common import APIResponse
from supabase import Client
from loguru import logger

router = APIRouter()


@router.post("/request", response_model=APIResponse[dict])
async def request_verification(
    body: Dict[str, Any],
    current_user=Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("verification:request")),
):
    """Submit verification documents and create an admin review notification.
    Body example:
    {
      "documents": [{"file_name":"...","file_path":"...","file_type":"verification","file_size":1234}],
      "notes": "..."
    }
    """
    try:
        docs: List[Dict[str, Any]] = body.get("documents", [])
        to_insert = []
        for d in docs:
            to_insert.append(
                {
                    "file_name": d.get("file_name"),
                    "file_path": d.get("file_path"),
                    "file_size": d.get("file_size"),
                    "file_type": d.get("file_type", "verification"),
                    "uploaded_by": current_user["id"],
                }
            )
        if to_insert:
            db.table("attachments").insert(to_insert).execute()
        # Notify admins by creating a special notification record for current user (admin dashboards can aggregate by type)
        db.table("notifications").insert(
            {
                "user_id": current_user["id"],
                "type": "verification_request",
                "title": "Company verification requested",
                "message": body.get("notes", ""),
                "data": {
                    "company_id": current_user.get("company_id"),
                    "documents": [d.get("file_name") for d in docs],
                },
            }
        ).execute()
        return APIResponse(success=True, data={"submitted": len(to_insert)})
    except Exception as e:
        logger.error(f"Verification request error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Doğrulama talebi oluşturulamadı")


@router.post("/approve", response_model=APIResponse[dict])
async def approve_verification(
    body: Dict[str, Any],
    current_user=Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("verification:review")),
):
    """Approve a company's verification.
    Body example: {"company_id":"..."}
    """
    try:
        company_id = body.get("company_id")
        if not company_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="company_id gerekli")
        result = db.table("companies").update({"verified": True}).eq("id", company_id).execute()
        if not result.data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Şirket doğrulanamadı")
        return APIResponse(success=True, data={"company_id": company_id}, message="Şirket doğrulandı")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verification approve error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Doğrulama onayı sırasında hata oluştu")


@router.get("/requests", response_model=APIResponse[Dict[str, Any]])
async def list_verification_requests(
    page: int = 1,
    size: int = 20,
    current_user=Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("verification:review")),
):
    """List recent company verification requests (from notifications)."""
    try:
        offset = (page - 1) * size
        query = (
            db.table("notifications")
            .select("*")
            .eq("type", "verification_request")
            .order("created_at", desc=True)
            .range(offset, offset + size - 1)
        )
        result = query.execute()
        count = (
            db.table("notifications").select("id", count="exact").eq("type", "verification_request").execute()
        )
        return APIResponse(
            success=True,
            data={
                "items": result.data or [],
                "page": page,
                "size": size,
                "total": count.count or 0,
            },
        )
    except Exception as e:
        logger.error(f"List verification requests error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Kayıtlar alınamadı")


@router.post("/reject", response_model=APIResponse[dict])
async def reject_verification(
    body: Dict[str, Any],
    current_user=Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("verification:review")),
):
    """Reject a company's verification (sets verified=false and logs a notification)."""
    try:
        company_id = body.get("company_id")
        if not company_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="company_id gerekli")
        # Ensure verified is false
        db.table("companies").update({"verified": False}).eq("id", company_id).execute()
        # Notify (could target company admins; here log under current user for trace)
        db.table("notifications").insert(
            {
                "user_id": current_user["id"],
                "type": "verification_reject",
                "title": "Company verification rejected",
                "message": "Your verification request has been rejected.",
                "data": {"company_id": company_id},
            }
        ).execute()
        return APIResponse(success=True, data={"company_id": company_id}, message="Şirket doğrulaması reddedildi")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verification reject error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Doğrulama reddi sırasında hata oluştu")
