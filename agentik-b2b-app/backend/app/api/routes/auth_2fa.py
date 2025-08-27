from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import pyotp

from app.core.auth import get_current_user_profile
from app.core.database import get_db
from app.core.permissions import require_permission
from app.models.common import APIResponse
from supabase import Client
from loguru import logger

router = APIRouter()


@router.post("/setup", response_model=APIResponse[dict])
async def setup_2fa(
    current_user=Depends(get_current_user_profile),
    db: Client = Depends(get_db),
):
    try:
        secret = pyotp.random_base32()
        otpauth_url = pyotp.totp.TOTP(secret).provisioning_uri(name=current_user.get("email", "user"), issuer_name="Agentik B2B")
        # Save secret temporarily until user confirms
        db.table("users").update({"two_factor_secret": secret}).eq("id", current_user["id"]).execute()
        return APIResponse(success=True, data={"secret": secret, "otpauth_url": otpauth_url})
    except Exception as e:
        logger.error(f"2FA setup error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="2FA kurulumu başarısız")


@router.post("/enable", response_model=APIResponse[dict])
async def enable_2fa(
    body: Dict[str, Any],
    current_user=Depends(get_current_user_profile),
    db: Client = Depends(get_db),
):
    try:
        code = str(body.get("code", ""))
        # Get secret
        user = db.table("users").select("two_factor_secret").eq("id", current_user["id"]).single().execute()
        secret = user.data.get("two_factor_secret") if user.data else None
        if not secret:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA secret bulunamadı. Önce setup yapın.")
        totp = pyotp.TOTP(secret)
        if not totp.verify(code, valid_window=1):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Geçersiz doğrulama kodu")
        db.table("users").update({"two_factor_enabled": True}).eq("id", current_user["id"]).execute()
        return APIResponse(success=True, data={"enabled": True}, message="2FA etkinleştirildi")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"2FA enable error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="2FA etkinleştirme başarısız")


@router.post("/disable", response_model=APIResponse[dict])
async def disable_2fa(
    current_user=Depends(get_current_user_profile),
    db: Client = Depends(get_db),
):
    try:
        db.table("users").update({"two_factor_enabled": False, "two_factor_secret": None}).eq("id", current_user["id"]).execute()
        return APIResponse(success=True, data={"enabled": False}, message="2FA devre dışı bırakıldı")
    except Exception as e:
        logger.error(f"2FA disable error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="2FA devre dışı bırakma başarısız")

