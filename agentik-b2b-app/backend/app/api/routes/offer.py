from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID

from app.core.auth import get_current_user_profile
from app.core.database import get_db
from app.core.permissions import require_permission
from app.models.supplier import Offer, OfferCreate, OfferUpdate, OfferStatus
from app.models.common import APIResponse, PaginatedResponse, FilterParams
from supabase import Client
from loguru import logger

router = APIRouter()


@router.post("", response_model=APIResponse[Offer])
async def create_offer(
    offer_data: OfferCreate,
    current_user = Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("quote:create"))
):
    """Teklif oluştur"""
    try:
        # RFQ check
        rfq_check = (
            db.table("rfqs").select("id", "status").eq("id", str(offer_data.rfq_id)).single().execute()
        )
        if not rfq_check.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RFQ bulunamadı")
        if rfq_check.data["status"] not in ["published", "in_review"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu RFQ için teklif verilemez")

        # Supplier check
        supplier_check = (
            db.table("suppliers").select("id", "company_id").eq("id", str(offer_data.supplier_id)).single().execute()
        )
        if not supplier_check.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tedarikçi bulunamadı")
        if supplier_check.data["company_id"] != current_user["company_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu tedarikçi hesabı için teklif verme yetkiniz yok",
            )

        # Prevent duplicates
        existing_offer = (
            db.table("offers")
            .select("id")
            .eq("rfq_id", str(offer_data.rfq_id))
            .eq("supplier_id", str(offer_data.supplier_id))
            .execute()
        )
        if existing_offer.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Bu RFQ için zaten teklifiniz bulunmaktadır"
            )

        create_data = offer_data.dict()
        create_data["status"] = OfferStatus.DRAFT.value
        result = db.table("offers").insert(create_data).execute()
        if not result.data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Teklif oluşturulamadı")

        offer_detail = (
            db.table("offers")
            .select("*", "rfqs(*)", "suppliers(*, companies(*))")
            .eq("id", result.data[0]["id"])
            .single()
            .execute()
        )
        return APIResponse(success=True, data=offer_detail.data, message="Teklif başarıyla oluşturuldu")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Offer creation error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Teklif oluşturulurken hata oluştu")


@router.get("", response_model=APIResponse[PaginatedResponse[Offer]])
async def get_offers(
    params: FilterParams = Depends(),
    status_filter: Optional[OfferStatus] = None,
    current_user = Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("quote:read"))
):
    """Teklif listeleme (kullanıcının şirketine göre)"""
    try:
        query = db.table("offers").select("*", "rfqs(*)", "suppliers(*, companies(*))")

        supplier_check = db.table("suppliers").select("id").eq("company_id", current_user["company_id"]).execute()
        if supplier_check.data:
            query = query.eq("suppliers.company_id", current_user["company_id"])
        else:
            query = query.eq("rfqs.company_id", current_user["company_id"])

        if status_filter:
            query = query.eq("status", status_filter.value)
        if params.search:
            query = query.ilike("notes", f"%{params.search}%")

        offset = (params.page - 1) * params.size
        query = query.range(offset, offset + params.size - 1)

        if params.sort_by:
            ascending = params.sort_order == "asc"
            query = query.order(params.sort_by, desc=not ascending)
        else:
            query = query.order("created_at", desc=True)

        result = query.execute()

        count_query = db.table("offers").select("id", count="exact")
        if supplier_check.data:
            count_query = count_query.eq("suppliers.company_id", current_user["company_id"])
        else:
            count_query = count_query.eq("rfqs.company_id", current_user["company_id"])
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
        logger.error(f"Offers list error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Teklif listesi alınırken hata oluştu")


@router.get("/by-rfq/{rfq_id}", response_model=APIResponse[List[Offer]])
async def get_offers_by_rfq(
    rfq_id: UUID,
    current_user = Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("quote:read"))
):
    """RFQ'ya ait teklifler"""
    try:
        rfq_check = db.table("rfqs").select("company_id").eq("id", str(rfq_id)).single().execute()
        if not rfq_check.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RFQ bulunamadı")
        if rfq_check.data["company_id"] != current_user["company_id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu RFQ'nun tekliflerini görme yetkiniz yok")

        result = (
            db.table("offers")
            .select("*", "suppliers(*, companies(*))")
            .eq("rfq_id", str(rfq_id))
            .order("price", desc=False)
            .execute()
        )
        return APIResponse(success=True, data=result.data or [])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Offers by RFQ error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="RFQ teklifleri alınırken hata oluştu")


@router.get("/{offer_id}", response_model=APIResponse[Offer])
async def get_offer_by_id(
    offer_id: UUID,
    current_user = Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("quote:read"))
):
    """Tek teklif detayı"""
    try:
        result = (
            db.table("offers")
            .select("*", "rfqs(*)", "suppliers(*, companies(*))")
            .eq("id", str(offer_id))
            .single()
            .execute()
        )
        if not result.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teklif bulunamadı")

        offer = result.data
        can_view = False
        if offer["rfqs"]["company_id"] == current_user["company_id"]:
            can_view = True
        elif offer["suppliers"]["company_id"] == current_user["company_id"]:
            can_view = True
        if not can_view:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu teklifi görme yetkiniz yok")

        return APIResponse(success=True, data=offer)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Offer detail error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Teklif detayları alınırken hata oluştu")


@router.put("/{offer_id}", response_model=APIResponse[Offer])
async def update_offer(
    offer_id: UUID,
    offer_update: OfferUpdate,
    current_user = Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("quote:update"))
):
    """Teklif güncelle"""
    try:
        offer_check = (
            db.table("offers").select("supplier_id", "status", "suppliers(company_id)").eq("id", str(offer_id)).single().execute()
        )
        if not offer_check.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teklif bulunamadı")

        if offer_check.data["suppliers"]["company_id"] != current_user["company_id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu teklifi güncelleme yetkiniz yok")

        update_data = {k: v for k, v in offer_update.dict().items() if v is not None}
        update_data["updated_at"] = "now()"

        result = db.table("offers").update(update_data).eq("id", str(offer_id)).execute()
        if not result.data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Teklif güncellenemedi")

        updated_offer = (
            db.table("offers").select("*", "rfqs(*)", "suppliers(*, companies(*))").eq("id", str(offer_id)).single().execute()
        )
        return APIResponse(success=True, data=updated_offer.data, message="Teklif başarıyla güncellendi")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Offer update error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Teklif güncellenirken hata oluştu")
