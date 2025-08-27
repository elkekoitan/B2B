from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from uuid import UUID

from app.core.auth import get_current_user_profile
from app.core.database import get_db
from app.core.permissions import require_permission
from app.models.catalog import CatalogItem, CatalogItemCreate, CatalogItemUpdate
from app.models.common import APIResponse, PaginatedResponse, FilterParams
from supabase import Client
from loguru import logger

router = APIRouter()


@router.get("/mine", response_model=APIResponse[PaginatedResponse[CatalogItem]])
async def my_catalog(
    params: FilterParams = Depends(),
    category: Optional[str] = None,
    currency: Optional[str] = None,
    current_user=Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("catalog:manage")),
):
    try:
        supplier = db.table("suppliers").select("id").eq("company_id", current_user["company_id"]).maybe_single().execute()
        if not supplier.data:
            return APIResponse(success=True, data=PaginatedResponse(data=[], total=0, page=params.page, size=params.size, has_next=False, has_previous=False))
        supplier_id = supplier.data["id"]
        query = db.table("supplier_products").select("*").eq("supplier_id", supplier_id)
        if category:
            query = query.eq("category", category)
        if currency:
            query = query.eq("currency", currency)
        if params.search:
            query = query.ilike("product_name", f"%{params.search}%")
        offset = (params.page - 1) * params.size
        query = query.range(offset, offset + params.size - 1)
        if params.sort_by:
            ascending = params.sort_order == "asc"
            query = query.order(params.sort_by, desc=not ascending)
        else:
            query = query.order("created_at", desc=True)
        result = query.execute()
        count_q = db.table("supplier_products").select("id", count="exact").eq("supplier_id", supplier_id)
        if category:
            count_q = count_q.eq("category", category)
        if currency:
            count_q = count_q.eq("currency", currency)
        count_result = count_q.execute()
        total = count_result.count or 0
        has_next = (params.page * params.size) < total
        has_previous = params.page > 1
        return APIResponse(
            success=True,
            data=PaginatedResponse(
                data=result.data or [], total=total, page=params.page, size=params.size, has_next=has_next, has_previous=has_previous
            ),
        )
    except Exception as e:
        logger.error(f"My catalog error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Katalog alınırken hata oluştu")


@router.get("/supplier/{supplier_id}", response_model=APIResponse[PaginatedResponse[CatalogItem]])
async def catalog_by_supplier(
    supplier_id: UUID,
    params: FilterParams = Depends(),
    category: Optional[str] = None,
    currency: Optional[str] = None,
    current_user=Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("supplier:read")),
):
    try:
        query = db.table("supplier_products").select("*").eq("supplier_id", str(supplier_id))
        if category:
            query = query.eq("category", category)
        if currency:
            query = query.eq("currency", currency)
        if params.search:
            query = query.ilike("product_name", f"%{params.search}%")
        offset = (params.page - 1) * params.size
        query = query.range(offset, offset + params.size - 1)
        query = query.order("created_at", desc=True)
        result = query.execute()
        count_q = db.table("supplier_products").select("id", count="exact").eq("supplier_id", str(supplier_id))
        if category:
            count_q = count_q.eq("category", category)
        if currency:
            count_q = count_q.eq("currency", currency)
        count_result = count_q.execute()
        total = count_result.count or 0
        has_next = (params.page * params.size) < total
        has_previous = params.page > 1
        return APIResponse(
            success=True,
            data=PaginatedResponse(
                data=result.data or [], total=total, page=params.page, size=params.size, has_next=has_next, has_previous=has_previous
            ),
        )
    except Exception as e:
        logger.error(f"Catalog by supplier error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Katalog alınırken hata oluştu")


@router.post("", response_model=APIResponse[CatalogItem])
async def create_catalog_item(
    item: CatalogItemCreate,
    current_user=Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("catalog:manage")),
):
    try:
        supplier = db.table("suppliers").select("company_id").eq("id", str(item.supplier_id)).single().execute()
        if not supplier.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tedarikçi bulunamadı")
        if supplier.data["company_id"] != current_user["company_id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu tedarikçinin kataloğunu yönetme yetkiniz yok")
        data = item.dict()
        result = db.table("supplier_products").insert(data).execute()
        if not result.data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Katalog ürünü oluşturulamadı")
        created = db.table("supplier_products").select("*").eq("id", result.data[0]["id"]).single().execute()
        return APIResponse(success=True, data=created.data, message="Katalog ürünü oluşturuldu")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create catalog item error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Katalog ürünü oluşturulurken hata oluştu")


@router.put("/{item_id}", response_model=APIResponse[CatalogItem])
async def update_catalog_item(
    item_id: UUID,
    updates: CatalogItemUpdate,
    current_user=Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("catalog:manage")),
):
    try:
        item_check = db.table("supplier_products").select("supplier_id", "suppliers(company_id)").eq("id", str(item_id)).single().execute()
        if not item_check.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Katalog ürünü bulunamadı")
        if item_check.data["suppliers"]["company_id"] != current_user["company_id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu katalog ürününü güncelleme yetkiniz yok")
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        result = db.table("supplier_products").update(update_data).eq("id", str(item_id)).execute()
        if not result.data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Katalog ürünü güncellenemedi")
        updated = db.table("supplier_products").select("*").eq("id", str(item_id)).single().execute()
        return APIResponse(success=True, data=updated.data, message="Katalog ürünü güncellendi")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update catalog item error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Katalog ürünü güncellenirken hata oluştu")


@router.delete("/{item_id}", response_model=APIResponse[dict])
async def delete_catalog_item(
    item_id: UUID,
    current_user=Depends(get_current_user_profile),
    db: Client = Depends(get_db),
    _perm_ok: bool = Depends(require_permission("catalog:manage")),
):
    try:
        item_check = db.table("supplier_products").select("supplier_id", "suppliers(company_id)").eq("id", str(item_id)).single().execute()
        if not item_check.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Katalog ürünü bulunamadı")
        if item_check.data["suppliers"]["company_id"] != current_user["company_id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu katalog ürününü silme yetkiniz yok")
        db.table("supplier_products").delete().eq("id", str(item_id)).execute()
        return APIResponse(success=True, data={"id": str(item_id)}, message="Katalog ürünü silindi")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete catalog item error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Katalog ürünü silinirken hata oluştu")
