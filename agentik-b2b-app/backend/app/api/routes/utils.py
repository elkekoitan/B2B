from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Dict

from app.core.auth import get_current_user_profile
from app.core.permissions import require_permission
from app.models.common import APIResponse
from app.services.currency import convert, DEFAULT_RATES_TO_USD
from app.core.config import settings
import os

router = APIRouter()


@router.get("/currency/rates", response_model=APIResponse[Dict[str, float]])
async def get_currency_rates(
    current_user=Depends(get_current_user_profile),
    _perm_ok: bool = Depends(require_permission("rfq:read")),
):
    return APIResponse(success=True, data=DEFAULT_RATES_TO_USD)


@router.get("/currency/convert", response_model=APIResponse[Dict[str, float]])
async def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
    current_user=Depends(get_current_user_profile),
    _perm_ok: bool = Depends(require_permission("rfq:read")),
):
    try:
        value = convert(amount, from_currency, to_currency)
        return APIResponse(success=True, data={"amount": value})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/upload", response_model=APIResponse[Dict[str, str]])
async def upload_file(
    f: UploadFile = File(...),
    current_user=Depends(get_current_user_profile),
    _perm_ok: bool = Depends(require_permission("verification:request")),
):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    dest = os.path.join(settings.UPLOAD_DIR, f.filename)
    content = await f.read()
    with open(dest, "wb") as out:
        out.write(content)
    return APIResponse(success=True, data={"file_name": f.filename, "file_path": dest})
