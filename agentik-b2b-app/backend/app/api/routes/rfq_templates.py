from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any

from app.core.permissions import require_permission
from app.services.rfq_templates import list_templates, get_template

router = APIRouter()


@router.get("", response_model=List[Dict[str, str]])
async def list_rfq_templates(_perm_ok: bool = Depends(require_permission("rfq:read"))):
    return list_templates()


@router.get("/{category}", response_model=Dict[str, Any])
async def get_rfq_template(category: str, _perm_ok: bool = Depends(require_permission("rfq:read"))):
    try:
        return get_template(category)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

