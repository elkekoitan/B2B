from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
import time
import traceback
from typing import Callable


class LoggingMiddleware(BaseHTTPMiddleware):
    """Request/Response logging middleware"""

    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        logger.info(
            f"Request: {request.method} {request.url} - Headers: {dict(request.headers)} - "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            logger.info(
                f"Response: {response.status_code} - Time: {process_time:.3f}s - Path: {request.url.path}"
            )
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url} - Error: {str(e)} - "
                f"Time: {process_time:.3f}s - Traceback: {traceback.format_exc()}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "error": "Internal server error",
                    "detail": "An unexpected error occurred",
                },
            )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Security headers middleware"""

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""

    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}

    async def dispatch(self, request: Request, call_next: Callable):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()

        # Clean old entries
        if client_ip in self.clients:
            self.clients[client_ip] = [
                timestamp
                for timestamp in self.clients[client_ip]
                if current_time - timestamp < self.period
            ]
        else:
            self.clients[client_ip] = []

        if len(self.clients[client_ip]) >= self.calls:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "error": "Rate limit exceeded",
                    "detail": f"Too many requests. Limit: {self.calls} per {self.period} seconds",
                },
            )

        self.clients[client_ip].append(current_time)
        return await call_next(request)

