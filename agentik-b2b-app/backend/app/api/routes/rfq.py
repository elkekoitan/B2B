from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from uuid import UUID

from app.core.auth import get_current_user_profile
from app.core.database import get_db
from app.core.permissions import require_permission
from app.models.rfq import (
    RFQ,
    RFQCreate,
    RFQUpdate,
    RFQDetail,
    RFQCreateWithTemplate,
)
from app.models.common import APIResponse, PaginatedResponse, FilterParams
from app.services.rfq_templates import get_template
from supabase import Client
from loguru import logger

router = APIRouter()


@router.post("", response_model=APIResponse[RFQ])
async def create_rfq(
    rfq_data: RFQCreate,
    current_user=Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("rfq:create")),
):
    try:
        create_data = rfq_data.dict()
        create_data.update(
            {
                "requester_id": current_user["id"],
                "company_id": current_user["company_id"],
                "status": "draft",
            }
        )
        result = db.table("rfqs").insert(create_data).execute()
        if not result.data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="RFQ oluşturulamadı")
        rfq_detail = (
            db.table("rfqs").select("*", "companies(*)").eq("id", result.data[0]["id"]).single().execute()
        )
        return APIResponse(success=True, data=rfq_detail.data, message="RFQ başarıyla oluşturuldu")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RFQ creation error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="RFQ oluşturulurken hata oluştu")


@router.post("/template", response_model=APIResponse[RFQ])
async def create_rfq_with_template(
    payload: RFQCreateWithTemplate,
    current_user=Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("rfq:create")),
):
    try:
        tpl = get_template(payload.category)
        required = [f["name"] for f in tpl.get("fields", []) if f.get("required")]
        missing = [name for name in required if name not in payload.extra_fields]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Eksik alanlar: {', '.join(missing)}",
            )

        create_data = {
            "title": payload.title,
            "description": payload.description,
            "category": payload.category,
            "quantity": payload.quantity,
            "unit": payload.unit,
            "currency": payload.currency,
            "budget_min": payload.budget_min,
            "budget_max": payload.budget_max,
            "deadline_date": str(payload.deadline_date) if payload.deadline_date else None,
            "delivery_location": payload.delivery_location,
            "priority": payload.priority,
            "attachments": payload.attachments,
            "requirements": {"template": payload.category, "fields": payload.extra_fields},
            "requester_id": current_user["id"],
            "company_id": current_user["company_id"],
            "status": "draft",
        }
        result = db.table("rfqs").insert(create_data).execute()
        if not result.data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="RFQ oluşturulamadı")
        rfq_detail = (
            db.table("rfqs").select("*", "companies(*)").eq("id", result.data[0]["id"]).single().execute()
        )
        return APIResponse(success=True, data=rfq_detail.data, message="RFQ başarıyla oluşturuldu")
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Şablon bulunamadı")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RFQ create via template error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="RFQ oluşturulurken hata oluştu")


@router.get("", response_model=APIResponse[PaginatedResponse[RFQ]])
async def get_rfqs(
    params: FilterParams = Depends(),
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    current_user=Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("rfq:read")),
):
    try:
        query = db.table("rfqs").select("*", "companies(*)")
        if category:
            query = query.eq("category", category)
        if status_filter:
            query = query.eq("status", status_filter)
        if params.search:
            query = query.ilike("title", f"%{params.search}%")
        offset = (params.page - 1) * params.size
        query = query.range(offset, offset + params.size - 1)
        if params.sort_by:
            ascending = params.sort_order == "asc"
            query = query.order(params.sort_by, desc=not ascending)
        else:
            query = query.order("created_at", desc=True)
        result = query.execute()
        count_result = db.table("rfqs").select("id", count="exact").execute()
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
        logger.error(f"RFQ list error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="RFQ listesi alınırken hata oluştu")


@router.get("/{rfq_id}", response_model=APIResponse[RFQDetail])
async def get_rfq_by_id(rfq_id: UUID, current_user=Depends(get_current_user_profile), db: Client = Depends(get_db)):
    try:
        result = db.table("rfqs").select("*", "companies(*)").eq("id", str(rfq_id)).single().execute()
        if not result.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RFQ bulunamadı")

        offers_stats = db.rpc("get_rfq_offer_stats", {"rfq_id": str(rfq_id)}).execute()
        rfq_data = result.data
        if offers_stats.data:
            stats = offers_stats.data[0] if offers_stats.data else {}
            rfq_data.update(
                {
                    "offer_count": stats.get("offer_count", 0),
                    "average_offer_price": stats.get("average_offer_price"),
                    "lowest_offer_price": stats.get("lowest_offer_price"),
                    "highest_offer_price": stats.get("highest_offer_price"),
                }
            )
        return APIResponse(success=True, data=rfq_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RFQ detail error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="RFQ detayları alınırken hata oluştu")


@router.put("/{rfq_id}", response_model=APIResponse[RFQ])
async def update_rfq(
    rfq_id: UUID,
    rfq_update: RFQUpdate,
    current_user=Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("rfq:update")),
):
    try:
        rfq_check = db.table("rfqs").select("requester_id").eq("id", str(rfq_id)).single().execute()
        if not rfq_check.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RFQ bulunamadı")
        if rfq_check.data["requester_id"] != current_user["id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu RFQ'yu güncelleme yetkiniz yok")
        update_data = {k: v for k, v in rfq_update.dict().items() if v is not None}
        update_data["updated_at"] = "now()"
        result = db.table("rfqs").update(update_data).eq("id", str(rfq_id)).execute()
        if not result.data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="RFQ güncellenemedi")
        updated_rfq = db.table("rfqs").select("*", "companies(*)").eq("id", str(rfq_id)).single().execute()
        return APIResponse(success=True, data=updated_rfq.data, message="RFQ başarıyla güncellendi")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RFQ update error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="RFQ güncellenirken hata oluştu")


@router.delete("/{rfq_id}", response_model=APIResponse[dict])
async def delete_rfq(
    rfq_id: UUID,
    current_user=Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("rfq:delete")),
):
    try:
        rfq_check = db.table("rfqs").select("requester_id", "status").eq("id", str(rfq_id)).single().execute()
        if not rfq_check.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RFQ bulunamadı")
        if rfq_check.data["requester_id"] != current_user["id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu RFQ'yu silme yetkiniz yok")
        if rfq_check.data["status"] == "awarded":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ödüllendirilmiş RFQ silinemez")
        result = db.table("rfqs").update({"status": "cancelled", "updated_at": "now()"}).eq("id", str(rfq_id)).execute()
        if not result.data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="RFQ silinemedi")
        return APIResponse(success=True, data={"id": str(rfq_id)}, message="RFQ başarıyla silindi")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RFQ delete error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="RFQ silinirken hata oluştu")


@router.post("/{rfq_id}/publish", response_model=APIResponse[RFQ])
async def publish_rfq(
    rfq_id: UUID,
    current_user=Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("rfq:update")),
):
    try:
        rfq_check = db.table("rfqs").select("requester_id", "status").eq("id", str(rfq_id)).single().execute()
        if not rfq_check.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RFQ bulunamadı")
        if rfq_check.data["requester_id"] != current_user["id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu RFQ'yu yayınlama yetkiniz yok")
        if rfq_check.data["status"] != "draft":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sadece taslak durumundaki RFQ'lar yayınlanabilir")
        result = db.table("rfqs").update({"status": "published", "updated_at": "now()"}).eq("id", str(rfq_id)).execute()
        if not result.data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="RFQ yayınlanamadı")
        published_rfq = db.table("rfqs").select("*", "companies(*)").eq("id", str(rfq_id)).single().execute()
        return APIResponse(success=True, data=published_rfq.data, message="RFQ başarıyla yayınlandı")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RFQ publish error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="RFQ yayınlanırken hata oluştu")
