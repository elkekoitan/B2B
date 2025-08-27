from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID

from app.core.auth import get_current_user_profile, get_optional_user
from app.core.database import get_db
from app.core.permissions import require_permission
from app.models.supplier import Supplier, SupplierCreate, SupplierUpdate
from app.models.common import APIResponse, PaginatedResponse, FilterParams
from supabase import Client
from loguru import logger

router = APIRouter()


@router.get("", response_model=APIResponse[PaginatedResponse[Supplier]])
async def get_suppliers(
    params: FilterParams = Depends(),
    industry: Optional[str] = None,
    verified: Optional[bool] = None,
    min_rating: Optional[float] = None,
    current_user = Depends(get_optional_user),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("supplier:read"))
):
    """Tedarikçi listesini getir"""
    try:
        query = db.table("suppliers").select("*", "companies(*)")

        if industry:
            query = query.eq("companies.industry", industry)
        if verified is not None:
            query = query.eq("verified", verified)
        if min_rating:
            query = query.gte("rating", min_rating)
        if params.search:
            query = query.or_(f"companies.name.ilike.%{params.search}%,specializations.cs.{{{params.search}}}")

        offset = (params.page - 1) * params.size
        query = query.range(offset, offset + params.size - 1)

        if params.sort_by:
            ascending = params.sort_order == "asc"
            query = query.order(params.sort_by, desc=not ascending)
        else:
            query = query.order("rating", desc=True)

        result = query.execute()

        count_query = db.table("suppliers").select("id", count="exact")
        if industry:
            count_query = count_query.eq("companies.industry", industry)
        if verified is not None:
            count_query = count_query.eq("verified", verified)
        if min_rating:
            count_query = count_query.gte("rating", min_rating)

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
            has_previous=has_previous
        )

        return APIResponse(success=True, data=paginated_data)

    except Exception as e:
        logger.error(f"Supplier list error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Tedarikçi listesi alınırken hata oluştu",
        )


@router.get("/{supplier_id}", response_model=APIResponse[Supplier])
async def get_supplier_by_id(
    supplier_id: UUID,
    current_user = Depends(get_optional_user),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("supplier:read"))
):
    """Tek tedarikçi detayını getir"""
    try:
        result = (
            db.table("suppliers")
            .select("*", "companies(*)")
            .eq("id", str(supplier_id))
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tedarikçi bulunamadı"
            )

        return APIResponse(success=True, data=result.data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Supplier detail error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Tedarikçi detayları alınırken hata oluştu",
        )


@router.post("", response_model=APIResponse[Supplier])
async def create_supplier(
    supplier_data: SupplierCreate,
    current_user = Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("profile:update"))
):
    """Yeni tedarikçi oluştur (kendi şirketini tedarikçi olarak kaydet)"""
    try:
        existing_supplier = (
            db.table("suppliers")
            .select("id")
            .eq("company_id", current_user["company_id"])
            .execute()
        )

        if existing_supplier.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Şirketiniz zaten tedarikçi olarak kayıtlı",
            )

        create_data = supplier_data.dict()
        create_data["company_id"] = current_user["company_id"]

        result = db.table("suppliers").insert(create_data).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tedarikçi oluşturulamadı",
            )

        supplier_detail = (
            db.table("suppliers")
            .select("*", "companies(*)")
            .eq("id", result.data[0]["id"])
            .single()
            .execute()
        )

        return APIResponse(
            success=True,
            data=supplier_detail.data,
            message="Tedarikçi kaydı başarıyla oluşturuldu",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Supplier creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Tedarikçi kaydı oluşturulurken hata oluştu",
        )


@router.put("/{supplier_id}", response_model=APIResponse[Supplier])
async def update_supplier(
    supplier_id: UUID,
    supplier_update: SupplierUpdate,
    current_user = Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("profile:update"))
):
    """Tedarikçi bilgilerini güncelle"""
    try:
        supplier_check = (
            db.table("suppliers")
            .select("company_id")
            .eq("id", str(supplier_id))
            .single()
            .execute()
        )

        if not supplier_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tedarikçi bulunamadı"
            )

        if supplier_check.data["company_id"] != current_user["company_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu tedarikçi profilini güncelleme yetkiniz yok",
            )

        update_data = {k: v for k, v in supplier_update.dict().items() if v is not None}
        update_data["updated_at"] = "now()"

        result = (
            db.table("suppliers")
            .update(update_data)
            .eq("id", str(supplier_id))
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tedarikçi bilgileri güncellenemedi",
            )

        updated_supplier = (
            db.table("suppliers").select("*", "companies(*)").eq("id", str(supplier_id)).single().execute()
        )

        return APIResponse(
            success=True,
            data=updated_supplier.data,
            message="Tedarikçi bilgileri başarıyla güncellendi",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Supplier update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Tedarikçi bilgileri güncellenirken hata oluştu",
        )


@router.get("/company/{company_id}", response_model=APIResponse[Supplier])
async def get_supplier_by_company(
    company_id: UUID,
    current_user = Depends(get_optional_user),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("supplier:read"))
):
    """Şirket ID'sine göre tedarikçi getir"""
    try:
        result = (
            db.table("suppliers").select("*", "companies(*)").eq("company_id", str(company_id)).single().execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bu şirket için tedarikçi kaydı bulunamadı",
            )

        return APIResponse(success=True, data=result.data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Supplier by company error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Tedarikçi bilgileri alınırken hata oluştu",
        )


@router.get("/search/specializations", response_model=APIResponse[List[str]])
async def get_specializations(
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("supplier:read"))
):
    """Mevcut uzmanlık alanlarını getir"""
    try:
        result = db.rpc("get_all_specializations").execute()
        specializations = result.data if result.data else []
        return APIResponse(success=True, data=specializations)
    except Exception as e:
        logger.error(f"Specializations error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Uzmanlık alanları alınırken hata oluştu",
        )

