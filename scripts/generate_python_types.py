#!/usr/bin/env python3
"""Generate Python enums and exceptions from protobuf definitions."""

import os
import sys
from pathlib import Path
import importlib.util

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from postfiat.logging import get_logger

def generate_enums_from_proto():
    """Generate postfiat/types/enums.py from protobuf enums."""

    # Import the generated protobuf module
    sys.path.insert(0, str(Path(__file__).parent.parent))

    try:
        from postfiat.v3 import messages_pb2, errors_pb2
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

    # Discover all enum types from all protobuf modules
    enum_types = {}
    protobuf_modules = [
        ('messages_pb2', messages_pb2),
        ('errors_pb2', errors_pb2)
    ]

    # Get all enum descriptors from all protobuf modules
    for module_name, module in protobuf_modules:
        print(f"🔍 Scanning {module_name} for enum types...")
        for name in dir(module):
            if not name.startswith('_'):
                attr = getattr(module, name)
                # Check if this is an enum type (EnumTypeWrapper with DESCRIPTOR)
                if hasattr(attr, 'DESCRIPTOR') and hasattr(attr.DESCRIPTOR, 'values_by_name'):
                    enum_types[name] = attr
                    print(f"📊 Found enum type: {name} in {module_name}")

    if not enum_types:
        print("⚠️  No enum types found in protobuf modules")
        return False

    # Generate enum classes dynamically
    for enum_name, enum_type in enum_types.items():
        # Get all enum values from the descriptor
        enum_values = []
        for value_name, value_descriptor in enum_type.DESCRIPTOR.values_by_name.items():
            enum_values.append((value_name, value_descriptor.number))

        # Sort by value to maintain consistent ordering
        enum_values.sort(key=lambda x: x[1])

        print(f"📝 Generating {enum_name} with {len(enum_values)} values")

        # Generate the enum class
        enums_code += f'class {enum_name}(IntEnum):\n'
        enums_code += f'    """{enum_name} enumeration from protobuf."""\n\n'

        for name, value in enum_values:
            enums_code += f'    {name} = {value}\n'

        enums_code += f'''
    @classmethod
    def from_protobuf(cls, pb_value) -> '{enum_name}':
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
    """Generate postfiat/exceptions.py from protobuf error definitions."""

    # Import the generated protobuf module
    sys.path.insert(0, str(Path(__file__).parent.parent))

    try:
        from postfiat.v3 import errors_pb2
    except ImportError as e:
        print(f"Error: Could not import errors_pb2: {e}")
        print("Make sure to run 'buf generate' first")
        return False

    print("🔍 Generating exceptions from protobuf error definitions...")

    # Start building the exceptions code
    exceptions_code = '''"""Auto-generated PostFiat SDK exceptions from protobuf definitions.

DO NOT EDIT - This file is auto-generated from proto files.
Run 'python scripts/generate_python_types.py' to regenerate.
"""

from typing import Optional, Any, Dict, Union
from enum import IntEnum


'''

    # Generate ErrorCode, ErrorCategory, and ErrorSeverity enums
    error_enums = ['ErrorCode', 'ErrorCategory', 'ErrorSeverity']
    for enum_name in error_enums:
        if hasattr(errors_pb2, enum_name):
            enum_type = getattr(errors_pb2, enum_name)
            enum_values = []
            for value_name, value_descriptor in enum_type.DESCRIPTOR.values_by_name.items():
                enum_values.append((value_name, value_descriptor.number))

            # Sort by value
            enum_values.sort(key=lambda x: x[1])

            exceptions_code += f'class {enum_name}(IntEnum):\n'
            exceptions_code += f'    """{enum_name} from protobuf error definitions."""\n\n'

            for name, value in enum_values:
                exceptions_code += f'    {name} = {value}\n'

            exceptions_code += '\n\n'

    # Generate base exception classes
    exceptions_code += '''class PostFiatError(Exception):
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


'''

    # Generate category-specific exception classes
    category_exceptions = {
        'CLIENT': ('ClientError', 'Base exception for client-side errors.'),
        'SERVER': ('ServerError', 'Base exception for server-side errors.'),
        'NETWORK': ('NetworkError', 'Network communication errors.'),
        'AUTH': ('AuthError', 'Authentication and authorization errors.'),
        'VALIDATION': ('ValidationError', 'Data validation errors.'),
        'CONFIGURATION': ('ConfigurationError', 'Configuration or setup errors.'),
        'BUSINESS': ('BusinessError', 'Business logic errors.'),
        'EXTERNAL': ('ExternalError', 'External service errors.')
    }

    for category_name, (class_name, doc) in category_exceptions.items():
        exceptions_code += f'''class {class_name}(PostFiatError):
    """{doc}"""

    def __init__(self, message: str, error_code: Optional[Union[int, 'ErrorCode']] = None, **kwargs):
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.{category_name},
            **kwargs
        )


'''

    # Generate specific exception classes for common error codes
    specific_exceptions = [
        ('AuthenticationError', 'AuthError', 'AUTHENTICATION_FAILED', 'Authentication failed.'),
        ('AuthorizationError', 'AuthError', 'AUTHORIZATION_FAILED', 'Authorization failed.'),
        ('ValidationFailedError', 'ValidationError', 'VALIDATION_FAILED', 'Data validation failed.'),
        ('ResourceNotFoundError', 'ClientError', 'RESOURCE_NOT_FOUND', 'Requested resource not found.'),
        ('InternalServerError', 'ServerError', 'INTERNAL_SERVER_ERROR', 'Internal server error occurred.'),
        ('ServiceUnavailableError', 'ServerError', 'SERVICE_UNAVAILABLE', 'Service temporarily unavailable.'),
        ('RateLimitError', 'ServerError', 'RATE_LIMIT_EXCEEDED', 'Rate limit exceeded.'),
        ('TimeoutError', 'ServerError', 'TIMEOUT', 'Operation timed out.'),
        ('ConnectionError', 'NetworkError', 'CONNECTION_FAILED', 'Network connection failed.'),
    ]

    for class_name, parent_class, error_code, doc in specific_exceptions:
        exceptions_code += f'''class {class_name}({parent_class}):
    """{doc}"""

    def __init__(self, message: str, **kwargs):
        # Remove error_code from kwargs if present to avoid conflicts
        kwargs.pop('error_code', None)
        super().__init__(
            message=message,
            error_code=ErrorCode.{error_code},
            **kwargs
        )


'''

    # Add utility functions with logging
    exceptions_code += '''# Import logging for factory functions
from postfiat.logging import get_logger


def create_exception_from_error_code(
    error_code: Union[int, ErrorCode],
    message: str,
    **kwargs
) -> PostFiatError:
    """Create appropriate exception instance based on error code."""
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
