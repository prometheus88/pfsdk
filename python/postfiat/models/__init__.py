"""PostFiat SDK - Database models.

This module contains SQLModel database models generated from protobuf definitions.

DO NOT EDIT - This file is auto-generated from proto files.
Run 'python scripts/generate_python_types.py' to regenerate.
"""

# Import all generated models
try:
    from .generated import *
    from .generated import __all__ as _generated_all
    __all__ = _generated_all if _generated_all else []
except ImportError:
    # Models not generated yet
    __all__ = []
