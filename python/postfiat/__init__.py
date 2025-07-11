"""PostFiat Wallet SDK - Python SDK for PostFiat Wallet Protocol.

This SDK provides a complete implementation for interacting with PostFiat services,
including wallet management, messaging, and cryptographic operations.

Auto-generated from protobuf definitions.
DO NOT EDIT - This file is auto-generated from proto files.
Run 'python scripts/generate_python_types.py' to regenerate.
"""

__version__ = "0.2.0-rc2"

# Core functionality imports
from . import exceptions
from . import types
from . import client
from . import models
from . import v3

# Import commonly used exceptions
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

# Import commonly used types
from .types import (
    MessageType,
    EncryptionMode,
)

# Import client functionality
from .client.base import (
    BaseClient,
    ClientConfig,
)

# Import all v3 protobuf messages and enums
from .v3 import (
    messages_pb2,
    errors_pb2,
)

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
