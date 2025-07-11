"""Auto-generated PostFiat SDK exceptions from protobuf definitions.

DO NOT EDIT - This file is auto-generated from proto files.
Run 'python scripts/generate_python_types.py' to regenerate.
"""

from typing import Optional, Any, Dict, Union
from enum import IntEnum


class ErrorCode(IntEnum):
    """ErrorCode from protobuf error definitions."""

    SUCCESS = 0
    UNKNOWN_ERROR = 1000
    BAD_REQUEST = 1001
    INVALID_INPUT = 1002
    MISSING_PARAMETER = 1003
    INVALID_PARAMETER = 1004
    MALFORMED_REQUEST = 1005
    UNSUPPORTED_OPERATION = 1006
    RESOURCE_NOT_FOUND = 1007
    DUPLICATE_RESOURCE = 1008
    PRECONDITION_FAILED = 1009
    REQUEST_TOO_LARGE = 1010
    AUTHENTICATION_REQUIRED = 2001
    AUTHENTICATION_FAILED = 2002
    INVALID_CREDENTIALS = 2003
    TOKEN_EXPIRED = 2004
    TOKEN_INVALID = 2005
    SESSION_EXPIRED = 2006
    ACCOUNT_LOCKED = 2007
    ACCOUNT_DISABLED = 2008
    AUTHORIZATION_FAILED = 3001
    INSUFFICIENT_PERMISSIONS = 3002
    ACCESS_DENIED = 3003
    RESOURCE_FORBIDDEN = 3004
    OPERATION_NOT_ALLOWED = 3005
    VALIDATION_FAILED = 4001
    SCHEMA_VALIDATION_FAILED = 4002
    TYPE_MISMATCH = 4003
    VALUE_OUT_OF_RANGE = 4004
    INVALID_FORMAT = 4005
    CONSTRAINT_VIOLATION = 4006
    REQUIRED_FIELD_MISSING = 4007
    INTERNAL_SERVER_ERROR = 5001
    SERVICE_UNAVAILABLE = 5002
    DATABASE_ERROR = 5003
    CONFIGURATION_ERROR = 5004
    DEPENDENCY_FAILURE = 5005
    RESOURCE_EXHAUSTED = 5006
    TIMEOUT = 5007
    DEADLOCK = 5008
    NETWORK_ERROR = 6001
    CONNECTION_FAILED = 6002
    CONNECTION_TIMEOUT = 6003
    CONNECTION_REFUSED = 6004
    DNS_RESOLUTION_FAILED = 6005
    SSL_ERROR = 6006
    PROTOCOL_ERROR = 6007
    BUSINESS_RULE_VIOLATION = 7001
    EXTERNAL_SERVICE_ERROR = 8001
    EXTERNAL_SERVICE_UNAVAILABLE = 8002
    EXTERNAL_SERVICE_TIMEOUT = 8003
    EXTERNAL_API_ERROR = 8004
    THIRD_PARTY_FAILURE = 8005
    RATE_LIMIT_EXCEEDED = 9001
    QUOTA_EXCEEDED = 9002
    THROTTLED = 9003


class ErrorCategory(IntEnum):
    """ErrorCategory from protobuf error definitions."""

    UNKNOWN = 0
    CLIENT = 1
    SERVER = 2
    NETWORK = 3
    AUTH = 4
    VALIDATION = 5
    CONFIGURATION = 6
    BUSINESS = 7
    EXTERNAL = 8


class ErrorSeverity(IntEnum):
    """ErrorSeverity from protobuf error definitions."""

    INFO = 0
    WARNING = 1
    ERROR = 2
    CRITICAL = 3
    FATAL = 4


class PostFiatError(Exception):
    """Base exception for all PostFiat SDK errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[Union[int, 'ErrorCode']] = None,
        category: Optional[Union[int, 'ErrorCategory']] = None,
        severity: Optional[Union[int, 'ErrorSeverity']] = None,
        details: Optional[Dict[str, Any]] = None,
        field: Optional[str] = None,
        error_id: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = ErrorCode(error_code) if error_code is not None else None
        self.category = ErrorCategory(category) if category is not None else None
        self.severity = ErrorSeverity(severity) if severity is not None else ErrorSeverity.ERROR
        self.details = details or {}
        self.field = field
        self.error_id = error_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary representation."""
        from postfiat.logging import get_logger
        logger = get_logger("exceptions.serialization")

        result = {
            'message': self.message,
            'error_code': self.error_code.value if self.error_code else None,
            'category': self.category.value if self.category else None,
            'severity': self.severity.value if self.severity else None,
            'details': self.details,
            'field': self.field,
            'error_id': self.error_id
        }

        logger.debug(
            "Serialized exception to dictionary",
            exception_type=self.__class__.__name__,
            error_code=result['error_code'],
            has_details=bool(self.details),
            has_field=bool(self.field),
            has_error_id=bool(self.error_id)
        )

        return result


class ClientError(PostFiatError):
    """Base exception for client-side errors."""

    def __init__(self, message: str, error_code: Optional[Union[int, 'ErrorCode']] = None, **kwargs):
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.CLIENT,
            **kwargs
        )


class ServerError(PostFiatError):
    """Base exception for server-side errors."""

    def __init__(self, message: str, error_code: Optional[Union[int, 'ErrorCode']] = None, **kwargs):
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.SERVER,
            **kwargs
        )


class NetworkError(PostFiatError):
    """Network communication errors."""

    def __init__(self, message: str, error_code: Optional[Union[int, 'ErrorCode']] = None, **kwargs):
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.NETWORK,
            **kwargs
        )


class AuthError(PostFiatError):
    """Authentication and authorization errors."""

    def __init__(self, message: str, error_code: Optional[Union[int, 'ErrorCode']] = None, **kwargs):
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.AUTH,
            **kwargs
        )


class ValidationError(PostFiatError):
    """Data validation errors."""

    def __init__(self, message: str, error_code: Optional[Union[int, 'ErrorCode']] = None, **kwargs):
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.VALIDATION,
            **kwargs
        )


class ConfigurationError(PostFiatError):
    """Configuration or setup errors."""

    def __init__(self, message: str, error_code: Optional[Union[int, 'ErrorCode']] = None, **kwargs):
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.CONFIGURATION,
            **kwargs
        )


class BusinessError(PostFiatError):
    """Business logic errors."""

    def __init__(self, message: str, error_code: Optional[Union[int, 'ErrorCode']] = None, **kwargs):
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.BUSINESS,
            **kwargs
        )


class ExternalError(PostFiatError):
    """External service errors."""

    def __init__(self, message: str, error_code: Optional[Union[int, 'ErrorCode']] = None, **kwargs):
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.EXTERNAL,
            **kwargs
        )


class AuthenticationError(AuthError):
    """Authentication failed."""

    def __init__(self, message: str, **kwargs):
        # Remove error_code from kwargs if present to avoid conflicts
        kwargs.pop('error_code', None)
        super().__init__(
            message=message,
            error_code=ErrorCode.AUTHENTICATION_FAILED,
            **kwargs
        )


class AuthorizationError(AuthError):
    """Authorization failed."""

    def __init__(self, message: str, **kwargs):
        # Remove error_code from kwargs if present to avoid conflicts
        kwargs.pop('error_code', None)
        super().__init__(
            message=message,
            error_code=ErrorCode.AUTHORIZATION_FAILED,
            **kwargs
        )


class ValidationFailedError(ValidationError):
    """Data validation failed."""

    def __init__(self, message: str, **kwargs):
        # Remove error_code from kwargs if present to avoid conflicts
        kwargs.pop('error_code', None)
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_FAILED,
            **kwargs
        )


class ResourceNotFoundError(ClientError):
    """Requested resource not found."""

    def __init__(self, message: str, **kwargs):
        # Remove error_code from kwargs if present to avoid conflicts
        kwargs.pop('error_code', None)
        super().__init__(
            message=message,
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            **kwargs
        )


class InternalServerError(ServerError):
    """Internal server error occurred."""

    def __init__(self, message: str, **kwargs):
        # Remove error_code from kwargs if present to avoid conflicts
        kwargs.pop('error_code', None)
        super().__init__(
            message=message,
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            **kwargs
        )


class ServiceUnavailableError(ServerError):
    """Service temporarily unavailable."""

    def __init__(self, message: str, **kwargs):
        # Remove error_code from kwargs if present to avoid conflicts
        kwargs.pop('error_code', None)
        super().__init__(
            message=message,
            error_code=ErrorCode.SERVICE_UNAVAILABLE,
            **kwargs
        )


class RateLimitError(ServerError):
    """Rate limit exceeded."""

    def __init__(self, message: str, **kwargs):
        # Remove error_code from kwargs if present to avoid conflicts
        kwargs.pop('error_code', None)
        super().__init__(
            message=message,
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            **kwargs
        )


class TimeoutError(ServerError):
    """Operation timed out."""

    def __init__(self, message: str, **kwargs):
        # Remove error_code from kwargs if present to avoid conflicts
        kwargs.pop('error_code', None)
        super().__init__(
            message=message,
            error_code=ErrorCode.TIMEOUT,
            **kwargs
        )


class ConnectionError(NetworkError):
    """Network connection failed."""

    def __init__(self, message: str, **kwargs):
        # Remove error_code from kwargs if present to avoid conflicts
        kwargs.pop('error_code', None)
        super().__init__(
            message=message,
            error_code=ErrorCode.CONNECTION_FAILED,
            **kwargs
        )


def create_exception_from_error_code(
    error_code: Union[int, ErrorCode],
    message: str,
    **kwargs
) -> PostFiatError:
    """Create appropriate exception instance based on error code."""
    from postfiat.logging import get_logger
    logger = get_logger("exceptions.factory")

    if isinstance(error_code, int):
        error_code = ErrorCode(error_code)

    # Log exception creation
    logger.info(
        "Creating exception from error code",
        error_code=error_code.name if hasattr(error_code, 'name') else str(error_code),
        error_value=error_code.value if hasattr(error_code, 'value') else error_code,
        message=message,
        has_details=bool(kwargs.get('details')),
        has_field=bool(kwargs.get('field')),
        has_error_id=bool(kwargs.get('error_id'))
    )

    # Map error codes to specific exception classes
    exception_map = {
        ErrorCode.AUTHENTICATION_FAILED: AuthenticationError,
        ErrorCode.AUTHORIZATION_FAILED: AuthorizationError,
        ErrorCode.VALIDATION_FAILED: ValidationFailedError,
        ErrorCode.RESOURCE_NOT_FOUND: ResourceNotFoundError,
        ErrorCode.INTERNAL_SERVER_ERROR: InternalServerError,
        ErrorCode.SERVICE_UNAVAILABLE: ServiceUnavailableError,
        ErrorCode.RATE_LIMIT_EXCEEDED: RateLimitError,
        ErrorCode.TIMEOUT: TimeoutError,
        ErrorCode.CONNECTION_FAILED: ConnectionError,
    }

    exception_class = exception_map.get(error_code, PostFiatError)

    # Log which exception class was selected
    logger.debug(
        "Selected exception class",
        exception_class=exception_class.__name__,
        is_specific_exception=exception_class != PostFiatError
    )

    return exception_class(message, error_code=error_code, **kwargs)


def create_exception_from_error_info(error_info_dict: Dict[str, Any]) -> PostFiatError:
    """Create exception from ErrorInfo protobuf message dictionary."""
    from postfiat.logging import get_logger
    logger = get_logger("exceptions.error_info")

    # Log ErrorInfo processing
    logger.info(
        "Processing ErrorInfo to create exception",
        error_code=error_info_dict.get('code'),
        has_message=bool(error_info_dict.get('message')),
        has_context=bool(error_info_dict.get('context')),
        has_field=bool(error_info_dict.get('field')),
        has_error_id=bool(error_info_dict.get('error_id')),
        severity=error_info_dict.get('severity')
    )

    return create_exception_from_error_code(
        error_code=error_info_dict.get('code'),
        message=error_info_dict.get('message', 'Unknown error'),
        severity=error_info_dict.get('severity'),
        details=error_info_dict.get('context', {}),
        field=error_info_dict.get('field'),
        error_id=error_info_dict.get('error_id')
    )
