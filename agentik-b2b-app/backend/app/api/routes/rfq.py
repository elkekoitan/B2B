from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID

from app.core.auth import get_current_user_profile
from app.core.database import get_db
from app.models.rfq import RFQ, RFQCreate, RFQUpdate, RFQDetail
from app.models.common import APIResponse, PaginatedResponse, FilterParams
from supabase import Client
from loguru import logger

router = APIRouter()

@router.post("", response_model=APIResponse[RFQ])
async def create_rfq(
    rfq_data: RFQCreate,
    current_user = Depends(get_current_user_profile),
    db: Client = Depends(get_db)
):
    """RFQ oluştur"""
    try:
        # RFQ verilerini hazırla
        create_data = rfq_data.dict()
        create_data.update({
            "requester_id": current_user["id"],
            "company_id": current_user["company_id"],
            "status": "draft"
        })
        
        # Supabase'e kaydet
        result = db.table("rfqs").insert(create_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="RFQ oluşturulamadı"
            )
        
        # RFQ detaylarını getir
        rfq_detail = db.table("rfqs").select(
            "*", "companies(*)"
        ).eq("id", result.data[0]["id"]).single().execute()
        
        return APIResponse(
            success=True,
            data=rfq_detail.data,
            message="RFQ başarıyla oluşturuldu"
        )
        
    except Exception as e:
        logger.error(f"RFQ creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="RFQ oluşturulurken hata oluştu"
        )

@router.get("", response_model=APIResponse[PaginatedResponse[RFQ]])
async def get_rfqs(
    params: FilterParams = Depends(),
    category: Optional[str] = None,
    status: Optional[str] = None,
    current_user = Depends(get_current_user_profile),
    db: Client = Depends(get_db)
):
    """RFQ listesini getir (user bazlı RLS ile)"""
    try:
        # Query builder
        query = db.table("rfqs").select(
            "*", 
            "companies(*)"
        )
        
        # Filters
        if category:
            query = query.eq("category", category)
        if status:
            query = query.eq("status", status)
        if params.search:
            query = query.ilike("title", f"%{params.search}%")
        
        # Pagination
        offset = (params.page - 1) * params.size
        query = query.range(offset, offset + params.size - 1)
        
        # Sorting
        if params.sort_by:
            ascending = params.sort_order == "asc"
            query = query.order(params.sort_by, desc=not ascending)
        else:
            query = query.order("created_at", desc=True)\n        \n        # Execute query\n        result = query.execute()\n        \n        # Get total count\n        count_result = db.table("rfqs").select(\n            "id", count="exact"\n        ).execute()\n        \n        total = count_result.count or 0\n        has_next = (params.page * params.size) < total\n        has_previous = params.page > 1\n        \n        paginated_data = PaginatedResponse(\n            data=result.data or [],\n            total=total,\n            page=params.page,\n            size=params.size,\n            has_next=has_next,\n            has_previous=has_previous\n        )\n        \n        return APIResponse(\n            success=True,\n            data=paginated_data\n        )\n        \n    except Exception as e:\n        logger.error(f\"RFQ list error: {e}\")\n        raise HTTPException(\n            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,\n            detail=\"RFQ listesi alınırken hata oluştu\"\n        )\n\n@router.get(\"/{rfq_id}\", response_model=APIResponse[RFQDetail])\nasync def get_rfq_by_id(\n    rfq_id: UUID,\n    current_user = Depends(get_current_user_profile),\n    db: Client = Depends(get_db)\n):\n    \"\"\"Tek RFQ detayını getir\"\"\"\n    try:\n        # RFQ'yu getir\n        result = db.table(\"rfqs\").select(\n            \"*\", \"companies(*)\"\n        ).eq(\"id\", str(rfq_id)).single().execute()\n        \n        if not result.data:\n            raise HTTPException(\n                status_code=status.HTTP_404_NOT_FOUND,\n                detail=\"RFQ bulunamadı\"\n            )\n        \n        # Offer istatistikleri\n        offers_stats = db.rpc(\n            \"get_rfq_offer_stats\", \n            {\"rfq_id\": str(rfq_id)}\n        ).execute()\n        \n        rfq_data = result.data\n        if offers_stats.data:\n            stats = offers_stats.data[0] if offers_stats.data else {}\n            rfq_data.update({\n                \"offer_count\": stats.get(\"offer_count\", 0),\n                \"average_offer_price\": stats.get(\"average_offer_price\"),\n                \"lowest_offer_price\": stats.get(\"lowest_offer_price\"),\n                \"highest_offer_price\": stats.get(\"highest_offer_price\")\n            })\n        \n        return APIResponse(\n            success=True,\n            data=rfq_data\n        )\n        \n    except HTTPException:\n        raise\n    except Exception as e:\n        logger.error(f\"RFQ detail error: {e}\")\n        raise HTTPException(\n            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,\n            detail=\"RFQ detayları alınırken hata oluştu\"\n        )\n\n@router.put(\"/{rfq_id}\", response_model=APIResponse[RFQ])\nasync def update_rfq(\n    rfq_id: UUID,\n    rfq_update: RFQUpdate,\n    current_user = Depends(get_current_user_profile),\n    db: Client = Depends(get_db)\n):\n    \"\"\"RFQ güncelle\"\"\"\n    try:\n        # Yetki kontrolü - sadece oluşturan kişi güncelleyebilir\n        rfq_check = db.table(\"rfqs\").select(\"requester_id\").eq(\n            \"id\", str(rfq_id)\n        ).single().execute()\n        \n        if not rfq_check.data:\n            raise HTTPException(\n                status_code=status.HTTP_404_NOT_FOUND,\n                detail=\"RFQ bulunamadı\"\n            )\n        \n        if rfq_check.data[\"requester_id\"] != current_user[\"id\"]:\n            raise HTTPException(\n                status_code=status.HTTP_403_FORBIDDEN,\n                detail=\"Bu RFQ'yu güncelleme yetkiniz yok\"\n            )\n        \n        # Update data hazırla\n        update_data = {k: v for k, v in rfq_update.dict().items() if v is not None}\n        update_data[\"updated_at\"] = \"now()\"\n        \n        # Güncelle\n        result = db.table(\"rfqs\").update(update_data).eq(\n            \"id\", str(rfq_id)\n        ).execute()\n        \n        if not result.data:\n            raise HTTPException(\n                status_code=status.HTTP_400_BAD_REQUEST,\n                detail=\"RFQ güncellenemedi\"\n            )\n        \n        # Güncellenmiş RFQ'yu getir\n        updated_rfq = db.table(\"rfqs\").select(\n            \"*\", \"companies(*)\"\n        ).eq(\"id\", str(rfq_id)).single().execute()\n        \n        return APIResponse(\n            success=True,\n            data=updated_rfq.data,\n            message=\"RFQ başarıyla güncellendi\"\n        )\n        \n    except HTTPException:\n        raise\n    except Exception as e:\n        logger.error(f\"RFQ update error: {e}\")\n        raise HTTPException(\n            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,\n            detail=\"RFQ güncellenirken hata oluştu\"\n        )\n\n@router.delete(\"/{rfq_id}\", response_model=APIResponse[dict])\nasync def delete_rfq(\n    rfq_id: UUID,\n    current_user = Depends(get_current_user_profile),\n    db: Client = Depends(get_db)\n):\n    \"\"\"RFQ sil\"\"\"\n    try:\n        # Yetki kontrolü - sadece oluşturan kişi silebilir\n        rfq_check = db.table(\"rfqs\").select(\"requester_id\", \"status\").eq(\n            \"id\", str(rfq_id)\n        ).single().execute()\n        \n        if not rfq_check.data:\n            raise HTTPException(\n                status_code=status.HTTP_404_NOT_FOUND,\n                detail=\"RFQ bulunamadı\"\n            )\n        \n        if rfq_check.data[\"requester_id\"] != current_user[\"id\"]:\n            raise HTTPException(\n                status_code=status.HTTP_403_FORBIDDEN,\n                detail=\"Bu RFQ'yu silme yetkiniz yok\"\n            )\n        \n        # Awarded RFQ silinmez\n        if rfq_check.data[\"status\"] == \"awarded\":\n            raise HTTPException(\n                status_code=status.HTTP_400_BAD_REQUEST,\n                detail=\"Ödüllendirilmiş RFQ silinemez\"\n            )\n        \n        # Soft delete - status'u cancelled yap\n        result = db.table(\"rfqs\").update({\n            \"status\": \"cancelled\",\n            \"updated_at\": \"now()\"\n        }).eq(\"id\", str(rfq_id)).execute()\n        \n        if not result.data:\n            raise HTTPException(\n                status_code=status.HTTP_400_BAD_REQUEST,\n                detail=\"RFQ silinemedi\"\n            )\n        \n        return APIResponse(\n            success=True,\n            data={\"id\": str(rfq_id)},\n            message=\"RFQ başarıyla silindi\"\n        )\n        \n    except HTTPException:\n        raise\n    except Exception as e:\n        logger.error(f\"RFQ delete error: {e}\")\n        raise HTTPException(\n            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,\n            detail=\"RFQ silinirken hata oluştu\"\n        )\n\n@router.post(\"/{rfq_id}/publish\", response_model=APIResponse[RFQ])\nasync def publish_rfq(\n    rfq_id: UUID,\n    current_user = Depends(get_current_user_profile),\n    db: Client = Depends(get_db)\n):\n    \"\"\"RFQ'yu yayınla\"\"\"\n    try:\n        # Yetki kontrolü\n        rfq_check = db.table(\"rfqs\").select(\"requester_id\", \"status\").eq(\n            \"id\", str(rfq_id)\n        ).single().execute()\n        \n        if not rfq_check.data:\n            raise HTTPException(\n                status_code=status.HTTP_404_NOT_FOUND,\n                detail=\"RFQ bulunamadı\"\n            )\n        \n        if rfq_check.data[\"requester_id\"] != current_user[\"id\"]:\n            raise HTTPException(\n                status_code=status.HTTP_403_FORBIDDEN,\n                detail=\"Bu RFQ'yu yayınlama yetkiniz yok\"\n            )\n        \n        if rfq_check.data[\"status\"] != \"draft\":\n            raise HTTPException(\n                status_code=status.HTTP_400_BAD_REQUEST,\n                detail=\"Sadece taslak durumundaki RFQ'lar yayınlanabilir\"\n            )\n        \n        # Status'u published yap\n        result = db.table(\"rfqs\").update({\n            \"status\": \"published\",\n            \"updated_at\": \"now()\"\n        }).eq(\"id\", str(rfq_id)).execute()\n        \n        if not result.data:\n            raise HTTPException(\n                status_code=status.HTTP_400_BAD_REQUEST,\n                detail=\"RFQ yayınlanamadı\"\n            )\n        \n        # Güncellenmiş RFQ'yu getir\n        published_rfq = db.table(\"rfqs\").select(\n            \"*\", \"companies(*)\"\n        ).eq(\"id\", str(rfq_id)).single().execute()\n        \n        return APIResponse(\n            success=True,\n            data=published_rfq.data,\n            message=\"RFQ başarıyla yayınlandı\"\n        )\n        \n    except HTTPException:\n        raise\n    except Exception as e:\n        logger.error(f\"RFQ publish error: {e}\")\n        raise HTTPException(\n            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,\n            detail=\"RFQ yayınlanırken hata oluştu\"\n        )\n