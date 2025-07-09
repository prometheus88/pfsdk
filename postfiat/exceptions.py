"""Auto-generated PostFiat SDK exceptions.

DO NOT EDIT - This file is auto-generated.
Run 'python scripts/generate_python_types.py' to regenerate.
"""

from typing import Optional, Any, Dict


class PostFiatError(Exception):
    """Base exception for all PostFiat SDK errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ClientError(PostFiatError):
    """Base exception for client-side errors."""
    pass


class ServerError(PostFiatError):
    """Base exception for server-side errors."""
    pass


class NetworkError(ClientError):
    """Network communication errors."""
    pass


class AuthenticationError(ClientError):
    """Authentication failed."""
    pass


class AuthorizationError(ClientError):
    """Authorization/permission denied."""
    pass


class ConfigurationError(ClientError):
    """Configuration or setup errors."""
    pass


class ValidationError(ClientError):
    """Data validation errors."""
    pass


class ProtocolError(ServerError):
    """Protocol-level errors."""
    pass


class ServiceUnavailableError(ServerError):
    """Service temporarily unavailable."""
    pass


class RateLimitError(ServerError):
    """Rate limit exceeded."""
    pass
