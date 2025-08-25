from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from app.core.database import get_db
from typing import Optional, Dict, Any
from loguru import logger
import jwt
from datetime import datetime, timedelta
from app.core.config import settings

security = HTTPBearer()

class AuthService:
    """Authentication service"""
    
    @staticmethod
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Client = Depends(get_db)
    ) -> Dict[str, Any]:
        """Get current authenticated user"""
        try:
            token = credentials.credentials
            
            # Verify token with Supabase
            user_response = db.auth.get_user(token)
            
            if not user_response.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token"
                )
            
            # Get user profile from database
            user_profile = db.table("users").select(
                "*", 
                "companies(*)"
            ).eq("auth_user_id", user_response.user.id).maybe_single().execute()
            
            if not user_profile.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )
            
            return {
                "auth_user": user_response.user,
                "profile": user_profile.data
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
    
    @staticmethod
    async def get_optional_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: Client = Depends(get_db)
    ) -> Optional[Dict[str, Any]]:
        """Get current user if authenticated, otherwise None"""
        if not credentials:
            return None
        
        try:
            return await AuthService.get_current_user(credentials, db)
        except:
            return None
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

# Dependency functions
async def get_current_user(user_data = Depends(AuthService.get_current_user)):
    return user_data

async def get_current_user_profile(user_data = Depends(AuthService.get_current_user)):
    return user_data["profile"]

async def get_current_auth_user(user_data = Depends(AuthService.get_current_user)):
    return user_data["auth_user"]

async def get_optional_user(user_data = Depends(AuthService.get_optional_user)):
    return user_data