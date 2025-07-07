#!/usr/bin/env python3
"""
Proto Introspection Engine

Core introspection system for analyzing protobuf message descriptors
and extracting schema information dynamically.

This replaces the hardcoded field name approach with proper runtime
introspection of actual proto definitions.
"""

import inspect
import importlib
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Type, Union
from enum import Enum
from google.protobuf.message import Message
from google.protobuf.descriptor import FieldDescriptor, EnumDescriptor, Descriptor

from postfiat.logging import get_logger

logger = get_logger("proto.introspection")


class FieldType(Enum):
    """Proto field types for type-aware test generation."""
    STRING = FieldDescriptor.TYPE_STRING
    INT32 = FieldDescriptor.TYPE_INT32
    UINT32 = FieldDescriptor.TYPE_UINT32
    INT64 = FieldDescriptor.TYPE_INT64
    UINT64 = FieldDescriptor.TYPE_UINT64
    BOOL = FieldDescriptor.TYPE_BOOL
    BYTES = FieldDescriptor.TYPE_BYTES
    DOUBLE = FieldDescriptor.TYPE_DOUBLE
    FLOAT = FieldDescriptor.TYPE_FLOAT
    ENUM = FieldDescriptor.TYPE_ENUM
    MESSAGE = FieldDescriptor.TYPE_MESSAGE


class FieldLabel(Enum):
    """Proto field labels."""
    OPTIONAL = FieldDescriptor.LABEL_OPTIONAL
    REQUIRED = FieldDescriptor.LABEL_REQUIRED
    REPEATED = FieldDescriptor.LABEL_REPEATED


@dataclass
class EnumValueInfo:
    """Information about a proto enum value."""
    name: str
    number: int


@dataclass
class EnumInfo:
    """Information about a proto enum."""
    name: str
    full_name: str
    values: List[EnumValueInfo]
    
    def get_valid_values(self) -> List[int]:
        """Get list of valid enum values."""
        return [v.number for v in self.values]
    
    def get_default_value(self) -> int:
        """Get default enum value (usually 0)."""
        return self.values[0].number if self.values else 0


@dataclass
class FieldInfo:
    """Information about a proto field."""
    name: str
    number: int
    type: FieldType
    label: FieldLabel
    default_value: Any
    enum_type: Optional[EnumInfo] = None
    message_type: Optional['MessageSchema'] = None
    
    @property
    def is_repeated(self) -> bool:
        """Check if field is repeated."""
        return self.label == FieldLabel.REPEATED
    
    @property
    def is_optional(self) -> bool:
        """Check if field is optional."""
        return self.label == FieldLabel.OPTIONAL
    
    @property
    def is_enum(self) -> bool:
        """Check if field is an enum."""
        return self.type == FieldType.ENUM
    
    @property
    def is_message(self) -> bool:
        """Check if field is a nested message."""
        return self.type == FieldType.MESSAGE


@dataclass
class MessageSchema:
    """Complete schema information for a proto message."""
    name: str
    full_name: str
    module_name: str
    message_class: Type[Message]
    fields: List[FieldInfo]
    nested_types: List['MessageSchema']
    enum_types: List[EnumInfo]
    
    def get_field_by_name(self, name: str) -> Optional[FieldInfo]:
        """Get field info by name."""
        for field in self.fields:
            if field.name == name:
                return field
        return None
    
    def get_enum_fields(self) -> List[FieldInfo]:
        """Get all enum fields."""
        return [f for f in self.fields if f.is_enum]
    
    def get_message_fields(self) -> List[FieldInfo]:
        """Get all nested message fields."""
        return [f for f in self.fields if f.is_message]
    
    def get_repeated_fields(self) -> List[FieldInfo]:
        """Get all repeated fields."""
        return [f for f in self.fields if f.is_repeated]


class ProtoIntrospector:
    """Core introspection engine for proto messages."""
    
    def __init__(self):
        self.logger = get_logger("proto.introspector")
        self._message_cache: Dict[str, MessageSchema] = {}
        self._enum_cache: Dict[str, EnumInfo] = {}
    
    def discover_proto_messages(self, modules: List[Any]) -> List[Type[Message]]:
        """Discover all proto message classes in given modules."""
        messages = []
        
        for module in modules:
            module_name = getattr(module, '__name__', str(module))
            self.logger.info(f"Discovering proto messages in {module_name}")
            
            for attr_name in dir(module):
                if attr_name.startswith('_'):
                    continue
                    
                attr = getattr(module, attr_name)
                if self._is_proto_message_class(attr):
                    messages.append(attr)
                    self.logger.debug(f"Found proto message: {attr_name}")
        
        self.logger.info(f"Discovered {len(messages)} proto message classes")
        return messages
    
    def analyze_message(self, message_class: Type[Message]) -> MessageSchema:
        """Analyze a proto message class and extract complete schema."""
        full_name = message_class.DESCRIPTOR.full_name
        
        # Check cache first
        if full_name in self._message_cache:
            return self._message_cache[full_name]
        
        self.logger.debug(f"Analyzing message: {full_name}")
        
        descriptor = message_class.DESCRIPTOR
        module_name = message_class.__module__.split('.')[-1].replace('_pb2', '')
        
        # Analyze fields
        fields = []
        for field_desc in descriptor.fields:
            field_info = self._analyze_field(field_desc)
            fields.append(field_info)
        
        # Analyze nested types
        nested_types = []
        for nested_desc in descriptor.nested_types:
            # Create nested message class
            nested_class = getattr(message_class, nested_desc.name)
            nested_schema = self.analyze_message(nested_class)
            nested_types.append(nested_schema)
        
        # Analyze enum types
        enum_types = []
        for enum_desc in descriptor.enum_types:
            enum_info = self._analyze_enum(enum_desc)
            enum_types.append(enum_info)
        
        schema = MessageSchema(
            name=descriptor.name,
            full_name=full_name,
            module_name=module_name,
            message_class=message_class,
            fields=fields,
            nested_types=nested_types,
            enum_types=enum_types
        )
        
        # Cache the result
        self._message_cache[full_name] = schema
        
        self.logger.debug(f"Analyzed message {full_name}: {len(fields)} fields, "
                         f"{len(nested_types)} nested types, {len(enum_types)} enums")
        
        return schema
    
    def _analyze_field(self, field_desc: FieldDescriptor) -> FieldInfo:
        """Analyze a single proto field."""
        field_type = FieldType(field_desc.type)
        field_label = FieldLabel(field_desc.label)
        
        # Handle enum fields
        enum_type = None
        if field_type == FieldType.ENUM:
            enum_type = self._analyze_enum(field_desc.enum_type)
        
        # Handle message fields (nested types)
        message_type = None
        if field_type == FieldType.MESSAGE:
            # We'll resolve this later to avoid circular dependencies
            pass
        
        return FieldInfo(
            name=field_desc.name,
            number=field_desc.number,
            type=field_type,
            label=field_label,
            default_value=field_desc.default_value,
            enum_type=enum_type,
            message_type=message_type
        )
    
    def _analyze_enum(self, enum_desc: EnumDescriptor) -> EnumInfo:
        """Analyze a proto enum."""
        full_name = enum_desc.full_name
        
        # Check cache first
        if full_name in self._enum_cache:
            return self._enum_cache[full_name]
        
        values = []
        for value_desc in enum_desc.values:
            values.append(EnumValueInfo(
                name=value_desc.name,
                number=value_desc.number
            ))
        
        enum_info = EnumInfo(
            name=enum_desc.name,
            full_name=full_name,
            values=values
        )
        
        # Cache the result
        self._enum_cache[full_name] = enum_info
        
        return enum_info
    
    def _is_proto_message_class(self, obj: Any) -> bool:
        """Check if object is a proto message class."""
        return (
            inspect.isclass(obj) and
            issubclass(obj, Message) and
            hasattr(obj, 'DESCRIPTOR') and
            hasattr(obj.DESCRIPTOR, 'fields')
        )
    
    def get_field_info(self, message_class: Type[Message], field_name: str) -> Optional[FieldInfo]:
        """Get detailed info about a specific field."""
        schema = self.analyze_message(message_class)
        return schema.get_field_by_name(field_name)
    
    def discover_dependencies(self, message_class: Type[Message]) -> List[Type[Message]]:
        """Find all nested message dependencies."""
        dependencies = []
        schema = self.analyze_message(message_class)
        
        for field in schema.fields:
            if field.is_message and field.message_type:
                dependencies.append(field.message_type.message_class)
                # Recursively find dependencies
                nested_deps = self.discover_dependencies(field.message_type.message_class)
                dependencies.extend(nested_deps)
        
        return list(set(dependencies))  # Remove duplicates
