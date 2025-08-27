from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List, Dict, Any
import json
import os
from base64 import b64decode
from loguru import logger
from jose import jwt
import requests
from app.database import supabase

security = HTTPBearer()

class AuthError(Exception):
    """Custom authentication error"""
    pass

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")

# Define role permissions
ROLE_PERMISSIONS = {
    "admin": ["*"],
    "buyer": [
        "rfq:create", "rfq:read", "rfq:update", "rfq:delete",
        "supplier:read", "catalog:read", "offer:read", "verification:request"
    ],
    "supplier": [
        "rfq:read", "catalog:create", "catalog:read", "catalog:update", "catalog:delete",
        "offer:create", "offer:read", "offer:update", "verification:request"
    ],
    "manager": [
        "rfq:read", "rfq:approve", "supplier:read", "catalog:read",
        "offer:read", "user:manage", "analytics:read"
    ]
}

_JWKS_CACHE: Optional[dict] = None

def _get_jwks() -> Optional[dict]:
    """Fetch and cache JWKS from Supabase for production verification."""
    global _JWKS_CACHE
    if _JWKS_CACHE is not None:
        return _JWKS_CACHE
    if not SUPABASE_URL:
        return None
    jwks_url = f"{SUPABASE_URL}/auth/v1/keys"
    try:
        resp = requests.get(jwks_url, timeout=5)
        resp.raise_for_status()
        _JWKS_CACHE = resp.json()
        return _JWKS_CACHE
    except Exception as e:
        logger.error(f"Failed to fetch JWKS: {e}")
        return None

def _decode_jwt_payload_unsafe(token: str) -> dict:
    """Decode JWT payload without signature verification (development only)."""
    try:
        # Split token
        parts = token.split('.')
        if len(parts) != 3:
            raise AuthError("Invalid token format")
        
        # Decode payload
        payload = parts[1]
        # Add padding if necessary
        payload += '=' * (4 - len(payload) % 4)
        decoded = b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        logger.error(f"Token decode failed: {e}")
        raise AuthError("Invalid token")

def _verify_jwt_prod(token: str) -> dict:
    """Verify JWT using Supabase JWKS in production and return payload."""
    jwks = _get_jwks()
    if not jwks:
        raise AuthError("JWKS unavailable for token verification")
    try:
        # We skip audience verification unless configured; Supabase can omit aud
        payload = jwt.decode(token, jwks, algorithms=["RS256"], options={"verify_aud": False})
        return payload
    except Exception as e:
        logger.error(f"JWT verification failed: {e}")
        raise AuthError("Invalid token")

async def _get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user profile from database"""
    try:
        response = supabase.table("users").select("*").eq("id", user_id).maybe_single().execute()
        return response.data
    except Exception as e:
        logger.error(f"Failed to fetch user profile: {e}")
        return None

def _extract_user_from_payload(payload: dict) -> dict:
    user_id = payload.get('sub') or payload.get('user_id')
    email = payload.get('email')
    if not user_id:
        raise AuthError("Invalid token payload")
    return {
        "user_id": user_id,
        "email": email,
        "metadata": payload
    }

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current authenticated user from JWT token with role information"""
    try:
        token = credentials.credentials
        
        # Check for mock admin token first (for development)
        if ENVIRONMENT != "production" and token == "mock-admin-token":
            return {
                "user_id": "8559c7d9-4ce8-4902-8ab9-a52cecd65fc2",
                "email": "turhanhamza@gmail.com",
                "role": "admin",
                "metadata": {
                    "sub": "8559c7d9-4ce8-4902-8ab9-a52cecd65fc2",
                    "email": "turhanhamza@gmail.com",
                    "full_name": "Turhan Hamza",
                    "is_admin": True,
                    "role": "admin"
                }
            }
        
        # Choose verification based on environment
        if ENVIRONMENT == "production":
            payload = _verify_jwt_prod(token)
        else:
            payload = _decode_jwt_payload_unsafe(token)

        user = _extract_user_from_payload(payload)
        
        # Get user profile from database to fetch role information
        user_profile = await _get_user_profile(user["user_id"])
        if user_profile:
            user["role"] = user_profile.get("role", "user")
            user["company_id"] = user_profile.get("company_id")
            user["full_name"] = user_profile.get("full_name")
        else:
            user["role"] = "user"
            
        return user
        
    except AuthError as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal authentication error"
        )

async def get_current_user_optional(request: Request) -> Optional[dict]:
    """Get current user if authenticated, otherwise return None"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
            
        token = auth_header.split(" ")[1]
        
        # Check for mock admin token first (for development)
        if ENVIRONMENT != "production" and token == "mock-admin-token":
            return {
                "user_id": "8559c7d9-4ce8-4902-8ab9-a52cecd65fc2",
                "email": "turhanhamza@gmail.com",
                "role": "admin",
                "metadata": {
                    "sub": "8559c7d9-4ce8-4902-8ab9-a52cecd65fc2",
                    "email": "turhanhamza@gmail.com",
                    "full_name": "Turhan Hamza",
                    "is_admin": True,
                    "role": "admin"
                }
            }
        
        if ENVIRONMENT == "production":
            payload = _verify_jwt_prod(token)
        else:
            payload = _decode_jwt_payload_unsafe(token)

        user = _extract_user_from_payload(payload)
        
        # Get user profile from database to fetch role information
        user_profile = await _get_user_profile(user["user_id"])
        if user_profile:
            user["role"] = user_profile.get("role", "user")
            user["company_id"] = user_profile.get("company_id")
            user["full_name"] = user_profile.get("full_name")
        else:
            user["role"] = "user"
            
        return user
        
    except Exception:
        return None

async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Require admin permissions: role=admin or is_admin True"""
    is_admin = current_user.get("role") == "admin" or (
        current_user.get("metadata", {}).get("is_admin") or 
        current_user.get("metadata", {}).get("role") == "admin"
    )
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

def _has_permission(user_role: str, resource: str, action: str) -> bool:
    """Check if user role has permission for resource:action"""
    # Admin has all permissions
    if user_role == "admin":
        return True
    
    # Get permissions for the role
    permissions = ROLE_PERMISSIONS.get(user_role, [])
    
    # Check for wildcard permission
    if "*" in permissions:
        return True
    
    # Check for specific permission
    target = f"{resource}:{action}"
    if target in permissions:
        return True
    
    # Check for resource-level permission (e.g., "rfq:*")
    resource_wildcard = f"{resource}:*"
    if resource_wildcard in permissions:
        return True
    
    return False

def require_permission(resource: str, action: str):
    """RBAC guard. Disabled if PERMISSIONS_ENFORCED is not truthy."""
    enforce = os.getenv("PERMISSIONS_ENFORCED", "").lower() in {"1", "true", "yes"}
    async def _checker(current_user: dict = Depends(get_current_user)):
        if not enforce:
            return current_user
            
        user_role = current_user.get("role", "user")
        if not _has_permission(user_role, resource, action):
            raise HTTPException(status_code=403, detail="Forbidden: insufficient permissions")
        return current_user
    return _checker

def require_role(required_roles: List[str]):
    """Require user to have one of the specified roles"""
    async def _checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role", "user")
        if user_role not in required_roles and "*" not in required_roles:
            raise HTTPException(
                status_code=403, 
                detail=f"Access denied. Required roles: {', '.join(required_roles)}"
            )
        return current_user
    return _checker
