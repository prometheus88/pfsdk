"""Auto-generated Pydantic-compatible enums from protobuf definitions.

DO NOT EDIT - This file is auto-generated from proto files.
Run 'python scripts/generate_python_types.py' to regenerate.
"""

from enum import IntEnum
from typing import Union


class EncryptionMode(IntEnum):
    """EncryptionMode enumeration from protobuf."""

    NONE = 0
    PROTECTED = 1
    PUBLIC_KEY = 2

    @classmethod
    def from_protobuf(cls, pb_value) -> 'EncryptionMode':
        """Convert from protobuf enum to Pydantic enum."""
        return cls(int(pb_value))

    def to_protobuf(self):
        """Convert from Pydantic enum to protobuf enum."""
        return int(self)


class MessageType(IntEnum):
    """MessageType enumeration from protobuf."""

    CORE_MESSAGE = 0
    MULTIPART_MESSAGE_PART = 1
    RESERVED_100 = 100

    @classmethod
    def from_protobuf(cls, pb_value) -> 'MessageType':
        """Convert from protobuf enum to Pydantic enum."""
        return cls(int(pb_value))

    def to_protobuf(self):
        """Convert from Pydantic enum to protobuf enum."""
        return int(self)


class ErrorCategory(IntEnum):
    """ErrorCategory enumeration from protobuf."""

    UNKNOWN = 0
    CLIENT = 1
    SERVER = 2
    NETWORK = 3
    AUTH = 4
    VALIDATION = 5
    CONFIGURATION = 6
    BUSINESS = 7
    EXTERNAL = 8

    @classmethod
    def from_protobuf(cls, pb_value) -> 'ErrorCategory':
        """Convert from protobuf enum to Pydantic enum."""
        return cls(int(pb_value))

    def to_protobuf(self):
        """Convert from Pydantic enum to protobuf enum."""
        return int(self)


class ErrorCode(IntEnum):
    """ErrorCode enumeration from protobuf."""

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

    @classmethod
    def from_protobuf(cls, pb_value) -> 'ErrorCode':
        """Convert from protobuf enum to Pydantic enum."""
        return cls(int(pb_value))

    def to_protobuf(self):
        """Convert from Pydantic enum to protobuf enum."""
        return int(self)


class ErrorSeverity(IntEnum):
    """ErrorSeverity enumeration from protobuf."""

    INFO = 0
    WARNING = 1
    ERROR = 2
    CRITICAL = 3
    FATAL = 4

    @classmethod
    def from_protobuf(cls, pb_value) -> 'ErrorSeverity':
        """Convert from protobuf enum to Pydantic enum."""
        return cls(int(pb_value))

    def to_protobuf(self):
        """Convert from Pydantic enum to protobuf enum."""
        return int(self)




# Export all enum types
__all__ = ['EncryptionMode', 'MessageType', 'ErrorCategory', 'ErrorCode', 'ErrorSeverity']
