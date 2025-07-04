"""PostFiat SDK - Type definitions package.

This package contains auto-generated type definitions from protobuf files.
Run 'python scripts/generate_python_types.py' to regenerate the types.
"""

# Import generated enums if they exist
try:
    from .enums import MessageType, EncryptionMode
    __all__ = ["MessageType", "EncryptionMode"]
except ImportError:
    # Generated files don't exist yet
    __all__ = []
