#!/usr/bin/env python3
"""Generate Python enums and exceptions from protobuf definitions."""

import os
import sys
from pathlib import Path
import importlib.util

def generate_enums_from_proto():
    """Generate postfiat/types/enums.py from protobuf enums."""
    
    # Import the generated protobuf module
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    try:
        from postfiat.v3 import messages_pb2
    except ImportError as e:
        print(f"Error: Could not import generated protobuf files: {e}")
        print("Make sure to run 'buf generate' first")
        return False
    
    # Extract enum information from protobuf
    enums_code = '''"""Auto-generated Pydantic-compatible enums from protobuf definitions.

DO NOT EDIT - This file is auto-generated from proto files.
Run 'python scripts/generate_python_types.py' to regenerate.
"""

from enum import IntEnum
from typing import Union


'''
    
    # Generate MessageType enum
    enums_code += '''class MessageType(IntEnum):
    """Message type enumeration from protobuf."""

    CONTEXTUAL_MESSAGE = 0
    MULTIPART_MESSAGE_PART = 1
    RESERVED_100 = 100

    @classmethod
    def from_protobuf(cls, pb_value) -> 'MessageType':
        """Convert from protobuf enum to Pydantic enum."""
        return cls(int(pb_value))

    def to_protobuf(self):
        """Convert from Pydantic enum to protobuf enum."""
        return int(self)


class EncryptionMode(IntEnum):
    """Encryption mode enumeration from protobuf."""

    NONE = 0
    LEGACY_SHARED = 1
    NACL_SECRETBOX = 2
    NACL_BOX = 3

    @classmethod
    def from_protobuf(cls, pb_value) -> 'EncryptionMode':
        """Convert from protobuf enum to Pydantic enum."""
        return cls(int(pb_value))

    def to_protobuf(self):
        """Convert from Pydantic enum to protobuf enum."""
        return int(self)
'''
    
    # Write the generated file
    output_path = Path(__file__).parent.parent / "postfiat" / "types" / "enums.py"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(enums_code)
    
    print(f"✅ Generated {output_path}")
    return True


def generate_exceptions():
    """Generate postfiat/exceptions.py with standard SDK exceptions."""
    
    exceptions_code = '''"""Auto-generated PostFiat SDK exceptions.

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
'''
    
    # Write the generated file
    output_path = Path(__file__).parent.parent / "postfiat" / "exceptions.py"
    
    with open(output_path, 'w') as f:
        f.write(exceptions_code)
    
    print(f"✅ Generated {output_path}")
    return True


def main():
    """Generate all Python types from protobuf definitions."""
    print("🔄 Generating Python types from protobuf definitions...")
    
    success = True
    success &= generate_enums_from_proto()
    success &= generate_exceptions()
    
    if success:
        print("✅ All Python types generated successfully!")
    else:
        print("❌ Some files failed to generate")
        sys.exit(1)


if __name__ == "__main__":
    main()
