"""
Security Middleware
Handles API key validation and basic security
Flexible - can be configured via environment
"""
import os
import logging
from flask import request

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    def __init__(self, app=None):
        self.app = app
        self.api_key = os.getenv('API_KEY', '')
        self.require_api_key = os.getenv('REQUIRE_API_KEY', 'False').lower() == 'true'
        
        logger.info(f"Security Middleware initialized")
        logger.info(f"Require API Key: {self.require_api_key}")
        logger.info(f"API Key Set: {'Yes' if self.api_key else 'No'}")
    
    def check_request(self, request):
        """
        Check incoming request for security compliance
        Returns dict with blocked status if request should be blocked
        """
        # Skip for OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            return {"blocked": False}
        
        # Check API key if required
        if self.require_api_key and self.api_key:
            api_key = request.headers.get('X-API-Key') or request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not api_key:
                return {
                    "blocked": True,
                    "error": "missing_api_key",
                    "message": "API key is required",
                    "code": 401
                }
            
            if api_key != self.api_key:
                return {
                    "blocked": True,
                    "error": "invalid_api_key",
                    "message": "Invalid API key",
                    "code": 401
                }
        
        # Add more security checks here if needed
        # - Rate limiting
        # - IP whitelisting
        # - Request size limits
        # - etc.
        
        return {"blocked": False}
    
    def validate_origin(self, request):
        """
        Optional origin validation
        Can be enabled/disabled via environment
        """
        allowed_origins = os.getenv('ALLOWED_ORIGINS', '').split(',')
        
        # If no origins specified, allow all
        if not allowed_origins or not allowed_origins[0]:
            return True
        
        origin = request.headers.get('Origin') or request.headers.get('Referer', '')
        
        # If no origin header, can't validate
        if not origin:
            return True
        
        # Check if origin is allowed
        for allowed in allowed_origins:
            if allowed.strip() and origin.startswith(allowed.strip()):
                return True
        
        return False