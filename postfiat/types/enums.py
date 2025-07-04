"""Auto-generated Pydantic-compatible enums from protobuf definitions.

DO NOT EDIT - This file is auto-generated from proto files.
Run 'python scripts/generate_python_types.py' to regenerate.
"""

from enum import IntEnum
from typing import Union


class MessageType(IntEnum):
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
