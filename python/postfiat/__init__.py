"""PostFiat Wallet SDK - Python SDK for PostFiat Wallet Protocol.

This SDK provides a complete implementation for interacting with PostFiat services,
including wallet management, messaging, and cryptographic operations.

Auto-generated from protobuf definitions.
DO NOT EDIT - This file is auto-generated from proto files.
Run 'python scripts/generate_python_types.py' to regenerate.
"""

__version__ = "0.2.0-rc3"

# Core functionality imports - handle missing modules during generation
try:
    from . import exceptions
except ImportError:
    pass
try:
    from . import types
except ImportError:
    pass
try:
    from . import client
except ImportError:
    pass
try:
    from . import models
except ImportError:
    pass
try:
    from . import v3
except ImportError:
    pass

# Import commonly used exceptions - handle missing modules during generation
try:
    from .exceptions import (
        PostFiatError,
        ClientError,
        ServerError,
        NetworkError,
        AuthError,
        ValidationError,
        AuthenticationError,
        AuthorizationError,
        ResourceNotFoundError,
        InternalServerError,
        ServiceUnavailableError,
        RateLimitError,
        TimeoutError,
        ConnectionError,
        ConfigurationError,
        BusinessError,
        ExternalError,
        ValidationFailedError,
        ErrorCode,
        ErrorCategory,
        ErrorSeverity,
        create_exception_from_error_code,
        create_exception_from_error_info,
    )
except ImportError:
    # exceptions module not available during generation
    pass

# Import commonly used types - handle missing modules during generation
try:
    from .types import (
        MessageType,
        EncryptionMode,
    )
except ImportError:
    # types module not available during generation
    pass

# Import client functionality - handle missing modules during generation
try:
    from .client.base import (
        BaseClient,
        ClientConfig,
    )
except ImportError:
    # client module not available during generation
    pass

# Import all v3 protobuf messages and enums - handle missing modules during generation
try:
    from .v3 import (
        messages_pb2,
        errors_pb2,
    )
except ImportError:
    # v3 module not available during generation
    pass

# Export all for easy access
__all__ = [
    # Version
    "__version__",
    
    # Modules
    "exceptions",
    "types", 
    "client",
    "models",
    "v3",
    
    # Exceptions
    "PostFiatError",
    "ClientError",
    "ServerError", 
    "NetworkError",
    "AuthError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "ResourceNotFoundError",
    "InternalServerError",
    "ServiceUnavailableError",
    "RateLimitError",
    "TimeoutError",
    "ConnectionError",
    "ConfigurationError",
    "BusinessError",
    "ExternalError",
    "ValidationFailedError",
    
    # Error enums
    "ErrorCode",
    "ErrorCategory", 
    "ErrorSeverity",
    
    # Exception factories
    "create_exception_from_error_code",
    "create_exception_from_error_info",
    
    # Types
    "MessageType",
    "EncryptionMode",
    
    # Client
    "BaseClient",
    "ClientConfig",
    
    # Protobuf modules
    "messages_pb2",
    "errors_pb2",
]

# Re-export common classes at package level for convenience
# Use try/except to handle cases where protobuf generation might not have created all classes yet
try:
    from .v3.messages_pb2 import Envelope
    __all__.append("Envelope")
except (ImportError, AttributeError):
    pass

try:
    from .v3.messages_pb2 import ContextReference
    __all__.append("ContextReference")
except (ImportError, AttributeError):
    pass

try:
    from .v3.messages_pb2 import PostFiatEnvelopePayload
    __all__.append("PostFiatEnvelopePayload")
except (ImportError, AttributeError):
    pass

try:
    from .v3.errors_pb2 import ErrorInfo
    __all__.append("ErrorInfo")
except (ImportError, AttributeError):
    pass
