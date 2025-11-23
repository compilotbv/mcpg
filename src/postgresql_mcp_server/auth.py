"""
Authentication middleware for MCP server.
"""

import os
import secrets
from typing import Optional
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


class AuthManager:
    """Handles API key authentication."""
    
    def __init__(self):
        """Initialize auth manager with API key from environment."""
        self.api_key = os.getenv("MCP_API_KEY")
        if not self.api_key:
            # Generate a random API key if none provided
            self.api_key = secrets.token_urlsafe(32)
            print(f"⚠️  No MCP_API_KEY set. Generated key: {self.api_key}")
            print("   Add this to your .env file: MCP_API_KEY={self.api_key}")
    
    def verify_token(self, credentials: HTTPAuthorizationCredentials = Security(security)) -> bool:
        """
        Verify the API key from Authorization header.
        
        Args:
            credentials: Bearer token from request
            
        Returns:
            True if valid
            
        Raises:
            HTTPException: If token is invalid
        """
        if credentials.credentials != self.api_key:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )
        return True

