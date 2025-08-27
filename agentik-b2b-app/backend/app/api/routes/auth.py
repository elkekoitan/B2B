from fastapi import APIRouter, Depends, HTTPException, status
from app.core.auth import get_current_user_profile, get_current_auth_user
from app.core.database import get_db
from app.models.user import User, UserUpdate
from app.models.common import APIResponse
from supabase import Client
from loguru import logger


router = APIRouter()


@router.get("/me", response_model=APIResponse[User])
async def get_current_user(
    current_user=Depends(get_current_user_profile),
    db: Client = Depends(get_db),
):
    try:
        return APIResponse(success=True, data=current_user)
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Kullanıcı bilgileri alınırken hata oluştu")


@router.put("/me", response_model=APIResponse[User])
async def update_current_user(
    user_update: UserUpdate,
    current_user=Depends(get_current_user_profile),
    db: Client = Depends(get_db),
):
    try:
        update_data = {k: v for k, v in user_update.dict().items() if v is not None}
        update_data["updated_at"] = "now()"
        result = db.table("users").update(update_data).eq("id", current_user["id"]).execute()
        if not result.data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Kullanıcı bilgileri güncellenemedi")
        updated_user = db.table("users").select("*", "companies(*)").eq("id", current_user["id"]).single().execute()
        return APIResponse(success=True, data=updated_user.data, message="Kullanıcı bilgileri başarıyla güncellendi")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User update error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Kullanıcı bilgileri güncellenirken hata oluştu")


@router.post("/logout", response_model=APIResponse[dict])
async def logout(
    auth_user=Depends(get_current_auth_user),
    db: Client = Depends(get_db),
):
    try:
        db.auth.sign_out()
        return APIResponse(success=True, data={"message": "Successfully logged out"}, message="Başarıyla çıkış yapıldı")
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Çıkış yapılırken hata oluştu")

