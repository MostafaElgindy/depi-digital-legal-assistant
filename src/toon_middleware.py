"""
TOON Middleware for FastAPI
Handles automatic conversion of TOON requests and responses
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from toon_parser import serialize_toon, parse_toon
import json
import logging

logger = logging.getLogger(__name__)


class TOONMiddleware(BaseHTTPMiddleware):
    """Middleware to handle TOON content type"""
    
    async def dispatch(self, request: Request, call_next):
        # Note: Response conversion is handled directly in endpoints
        # This middleware can be extended for request parsing if needed
        
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Middleware error: {str(e)}")
            raise
