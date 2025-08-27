from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID

from app.core.auth import get_current_user_profile
from app.core.database import get_db
from app.core.permissions import require_permission
from app.models.email import EmailLog, EmailType, EmailStatus
from app.models.common import APIResponse, PaginatedResponse, FilterParams
from supabase import Client
from loguru import logger

router = APIRouter()


@router.get("/logs", response_model=APIResponse[PaginatedResponse[EmailLog]])
async def get_email_logs(
    params: FilterParams = Depends(),
    email_type: Optional[EmailType] = None,
    status_filter: Optional[EmailStatus] = None,
    current_user = Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("email:read")),
):
    try:
        query = db.table("email_logs").select("*")
        if email_type:
            query = query.eq("email_type", email_type.value)
        if status_filter:
            query = query.eq("status", status_filter.value)
        if params.search:
            query = query.or_(f"subject.ilike.%{params.search}%,recipient_email.ilike.%{params.search}%")
        offset = (params.page - 1) * params.size
        query = query.range(offset, offset + params.size - 1)
        if params.sort_by:
            ascending = params.sort_order == "asc"
            query = query.order(params.sort_by, desc=not ascending)
        else:
            query = query.order("created_at", desc=True)
        result = query.execute()
        count_query = db.table("email_logs").select("id", count="exact")
        if email_type:
            count_query = count_query.eq("email_type", email_type.value)
        if status_filter:
            count_query = count_query.eq("status", status_filter.value)
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
        logger.error(f"Email logs error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Email logları alınırken hata oluştu")


@router.get("/logs/{email_id}", response_model=APIResponse[EmailLog])
async def get_email_log_detail(
    email_id: UUID,
    current_user = Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("email:read")),
):
    try:
        result = db.table("email_logs").select("*").eq("id", str(email_id)).single().execute()
        if not result.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email log bulunamadı")
        return APIResponse(success=True, data=result.data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email log detail error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Email log detayları alınırken hata oluştu")


@router.post("/send-rfq-invitation", response_model=APIResponse[dict])
async def send_rfq_invitation(
    rfq_id: UUID,
    supplier_ids: List[UUID],
    current_user = Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("email:send")),
):
    try:
        rfq_check = db.table("rfqs").select("company_id", "title", "status").eq("id", str(rfq_id)).single().execute()
        if not rfq_check.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RFQ bulunamadı")
        if rfq_check.data["company_id"] != current_user["company_id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu RFQ için davetiye gönderme yetkiniz yok")
        if rfq_check.data["status"] != "published":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sadece yayınlanmış RFQ'lar için davetiye gönderilebilir")

        suppliers = (
            db.table("suppliers").select("id", "companies(email, name)").in_("id", [str(sid) for sid in supplier_ids]).execute()
        )
        if not suppliers.data or len(suppliers.data) != len(supplier_ids):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bazı tedarikçiler bulunamadı")

        sent_count = 0
        failed_suppliers: List[str] = []
        for supplier in suppliers.data:
            try:
                invitation_data = {
                    "rfq_id": str(rfq_id),
                    "supplier_id": supplier["id"],
                    "invited_by": current_user["id"],
                    "status": "sent",
                }
                db.table("rfq_invitations").insert(invitation_data).execute()
                email_log_data = {
                    "sender_email": current_user["email"],
                    "recipient_email": supplier["companies"]["email"],
                    "subject": f"RFQ Davetiyesi: {rfq_check.data['title']}",
                    "body": f"Sayın {supplier['companies']['name']}, {rfq_check.data['title']} başlıklı RFQ için teklifinizi bekliyoruz.",
                    "email_type": "rfq_invitation",
                    "rfq_id": str(rfq_id),
                    "status": "pending",
                }
                db.table("email_logs").insert(email_log_data).execute()
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send invitation to supplier {supplier['id']}: {e}")
                failed_suppliers.append(supplier["companies"]["name"])

        return APIResponse(
            success=True,
            data={"sent_count": sent_count, "total_suppliers": len(supplier_ids), "failed_suppliers": failed_suppliers},
            message=f"{sent_count} tedarikçiye davetiye gönderildi" + (f", {len(failed_suppliers)} gönderilemedi" if failed_suppliers else ""),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RFQ invitation error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="RFQ davetiyesi gönderilirken hata oluştu")


@router.get("/invitations/{rfq_id}", response_model=APIResponse[List[dict]])
async def get_rfq_invitations(
    rfq_id: UUID,
    current_user = Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("email:read")),
):
    try:
        rfq_check = db.table("rfqs").select("company_id").eq("id", str(rfq_id)).single().execute()
        if not rfq_check.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RFQ bulunamadı")
        if rfq_check.data["company_id"] != current_user["company_id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu RFQ'nun davetiyelerini görme yetkiniz yok")
        result = (
            db.table("rfq_invitations")
            .select("*", "suppliers(*, companies(*))")
            .eq("rfq_id", str(rfq_id))
            .order("created_at", desc=True)
            .execute()
        )
        return APIResponse(success=True, data=result.data or [])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RFQ invitations error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="RFQ davetiyeleri alınırken hata oluştu")


@router.get("/stats", response_model=APIResponse[dict])
async def get_email_stats(
    current_user = Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("email:read")),
):
    try:
        total_emails = db.table("email_logs").select("id", count="exact").execute()
        sent_emails = db.table("email_logs").select("id", count="exact").eq("status", "sent").execute()
        return APIResponse(success=True, data={"total": total_emails.count or 0, "sent": sent_emails.count or 0})
    except Exception as e:
        logger.error(f"Email stats error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Email istatistikleri alınırken hata oluştu")

