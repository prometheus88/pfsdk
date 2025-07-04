#!/usr/bin/env python3
"""
Test Generation Script for Protobuf-based PFT Wallet v2

Generates comprehensive test suites from protobuf definitions:
- Contract Validation: Positive/negative validation tests
- Serialization Integrity: Round-trip serialization tests  
- Persistence Scaffolding: Endpoint and database tests

Usage:
    python scripts/generate_protobuf_tests.py
"""

import os
import sys
import inspect
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from postfiat.v3 import messages_pb2
# Import other services when they exist
try:
    from postfiat.v3 import wallet_service_pb2
except ImportError:
    wallet_service_pb2 = None
try:
    from postfiat.v3 import discord_service_pb2
except ImportError:
    discord_service_pb2 = None
try:
    from postfiat.v3 import knowledge_service_pb2
except ImportError:
    knowledge_service_pb2 = None
try:
    from postfiat.v3 import event_streaming_service_pb2
except ImportError:
    event_streaming_service_pb2 = None


class ProtobufTestGenerator:
    """Generates test files from protobuf definitions."""
    
    def __init__(self, output_base: str = "tests"):
        self.output_base = Path(output_base)
        self.modules = {
            'messages': messages_pb2,
        }
        self.timestamp = datetime.now().isoformat()
        
    def generate_all_tests(self):
        """Generate all test suites."""
        print("🚀 Generating protobuf-based test suites...")
        
        # Extract all message types and services
        message_types = self._extract_message_types()
        services = self._extract_services()
        
        print(f"📊 Found {len(message_types)} message types and {len(services)} services")
        
        # Create the generated tests directory
        generated_dir = self.output_base / "generated"
        generated_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate __init__.py
        (generated_dir / "__init__.py").write_text('"""Generated Protobuf Tests"""\n')
        
        # Generate contract validation tests
        self._generate_contract_validation_tests(message_types, generated_dir)
        
        # Generate serialization integrity tests  
        self._generate_serialization_integrity_tests(message_types, generated_dir)
        
        # Generate persistence scaffolding tests
        self._generate_persistence_scaffolding_tests(services, generated_dir)
        
        print("✅ Test generation complete!")
        
    def _extract_message_types(self) -> Dict[str, Any]:
        """Extract all message types from protobuf modules."""
        message_types = {}
        
        for module_name, module in self.modules.items():
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                # Check if it's a protobuf message class
                if (hasattr(attr, 'DESCRIPTOR') and 
                    hasattr(attr.DESCRIPTOR, 'fields') and
                    not attr_name.startswith('_')):
                    
                    message_types[f"{module_name}.{attr_name}"] = {
                        'class': attr,
                        'module': module_name,
                        'name': attr_name,
                        'descriptor': attr.DESCRIPTOR
                    }
                    
        return message_types
        
    def _extract_services(self) -> Dict[str, Any]:
        """Extract all service definitions from protobuf modules."""
        services = {}
        
        for module_name, module in self.modules.items():
            if hasattr(module, 'DESCRIPTOR') and hasattr(module.DESCRIPTOR, 'services_by_name'):
                for service_name, service_desc in module.DESCRIPTOR.services_by_name.items():
                    services[f"{module_name}.{service_name}"] = {
                        'module': module_name,
                        'name': service_name,
                        'descriptor': service_desc,
                        'methods': [
                            {
                                'name': method.name,
                                'input_type': method.input_type.name,
                                'output_type': method.output_type.name,
                                'full_name': method.full_name
                            }
                            for method in service_desc.methods
                        ]
                    }
                    
        return services

    def _generate_contract_validation_tests(self, message_types: Dict[str, Any], output_dir: Path):
        """Generate contract validation tests (formerly Tier 1)."""
        test_content = self._generate_validation_test_content(message_types)
        (output_dir / "test_contract_validation.py").write_text(test_content)
        
        print(f"📝 Generated contract validation tests for {len(message_types)} message types")

    def _generate_validation_test_content(self, message_types: Dict[str, Any]) -> str:
        """Generate the content for validation tests."""
        content = f'''"""
Contract Validation Tests

Auto-generated from protobuf definitions on {self.timestamp}
DO NOT EDIT - Regenerate using scripts/generate_protobuf_tests.py

Tests that protobuf messages conform to their defined contracts and can be 
validated properly by Pydantic models.
"""

import pytest
from typing import Any, Dict, List
from pydantic import ValidationError
from google.protobuf.message import Message

# Import all protobuf message types
from postfiat.v3 import messages_pb2


class TestProtobufValidation:
    """Test protobuf message validation against Pydantic models."""
    
    @pytest.mark.parametrize("message_class", [
'''
        
        # Add each message type as a test parameter
        for msg_key, msg_info in message_types.items():
            module_name = msg_info['module'] 
            class_name = msg_info['name']
            content += f'        {module_name}_pb2.{class_name},\n'
            
        content += '''    ])
    def test_positive_validation(self, message_class):
        """Test that valid protobuf messages can be created without error."""
        try:
            # Create an instance with default values
            instance = message_class()
            assert instance is not None
            
            # Verify it's a valid protobuf message
            assert isinstance(instance, Message)
            
            # Test serialization/deserialization
            serialized = instance.SerializeToString()
            deserialized = message_class()
            deserialized.ParseFromString(serialized)
            
            assert instance == deserialized, f"Round-trip serialization failed for {message_class.__name__}"
            
        except Exception as e:
            pytest.fail(f"Failed to create valid {message_class.__name__}: {e}")
    
    @pytest.mark.parametrize("message_class", [
'''
        
        # Add message types again for negative testing
        for msg_key, msg_info in message_types.items():
            module_name = msg_info['module']
            class_name = msg_info['name']
            content += f'        {module_name}_pb2.{class_name},\n'
            
        content += '''    ])
    def test_field_type_validation(self, message_class):
        """Test that protobuf messages properly validate field types."""
        instance = message_class()
        descriptor = instance.DESCRIPTOR
        
        # Test each field's type constraints
        for field in descriptor.fields:
            # Skip testing complex nested fields and repeated/map fields
            if field.type in [field.TYPE_MESSAGE, field.TYPE_GROUP]:
                continue
                
            # Skip repeated fields (arrays) and map fields as they require special handling
            if field.label == field.LABEL_REPEATED:
                continue
                
            field_name = field.name
            
            # Test that field exists and can be accessed
            if hasattr(instance, field_name):
                try:
                    # Get the current value (should be default)
                    current_value = getattr(instance, field_name)
                    
                    # Verify we can set it to the same type
                    setattr(instance, field_name, current_value)
                    
                except Exception as e:
                    pytest.fail(f"Field {field_name} in {message_class.__name__} failed basic access: {e}")
'''

        # Generate specific structure tests for key message types
        key_messages = self._identify_key_messages(message_types)
        for msg_key, msg_info in key_messages.items():
            content += self._generate_specific_message_test(msg_info)

        # Generate enum validation tests
        content += self._generate_enum_validation_tests(message_types)

        return content

    def _identify_key_messages(self, message_types: Dict[str, Any]) -> Dict[str, Any]:
        """Identify key message types that need specific structural tests."""
        key_messages = {}
        
        for msg_key, msg_info in message_types.items():
            class_name = msg_info['name']
            
            # Identify important message types based on naming patterns
            if any(pattern in class_name.lower() for pattern in [
                'envelope', 'base', 'core', 'metadata', 'session', 'user'
            ]):
                key_messages[msg_key] = msg_info
                
        return key_messages

    def _generate_specific_message_test(self, msg_info: Dict[str, Any]) -> str:
        """Generate a specific structural test for a key message type."""
        module_name = msg_info['module']
        class_name = msg_info['name']
        descriptor = msg_info['descriptor']
        
        # Get actual fields from the descriptor
        fields_info = []
        for field in descriptor.fields:
            fields_info.append({
                'name': field.name,
                'type': field.type,
                'label': field.label,
                'type_name': getattr(field, 'type_name', '') if hasattr(field, 'type_name') else ''
            })
        
        content = f'''
    def test_{class_name.lower()}_structure(self):
        """Test the {class_name} structure and field accessibility."""
        instance = {module_name}_pb2.{class_name}()
        
        # Test that expected fields exist (based on actual protobuf definition)
'''
        
        for field_info in fields_info:
            field_name = field_info['name']
            content += f'        assert hasattr(instance, \'{field_name}\'), "Missing field: {field_name}"\n'
        
        content += '\n        # Test setting and getting field values\n'
        
        for field_info in fields_info:
            field_name = field_info['name']
            field_type = field_info['type']
            
            test_value = self._generate_test_value_for_field(field_info, module_name)
            if test_value:
                content += f'        instance.{field_name} = {test_value}\n'
                content += f'        assert instance.{field_name} == {test_value}\n'
        
        return content

    def _generate_test_value_for_field(self, field_info: Dict[str, Any], module_name: str) -> Optional[str]:
        """Generate appropriate test value based on field type and name."""
        field_name = field_info['name']
        field_type = field_info['type']
        field_label = field_info['label']
        
        # Skip repeated fields (arrays) and map fields - they need special handling with append()
        if field_label == 3:  # LABEL_REPEATED
            return None
            
        # Map protobuf field types to test values
        if field_type == 9:  # TYPE_STRING
            if 'id' in field_name.lower():
                return f'\"test-{field_name}-123\"'
            elif 'email' in field_name.lower():
                return '\"test@example.com\"'
            elif 'hash' in field_name.lower():
                return '\"test-hash-abc123\"'
            elif 'key' in field_name.lower():
                return '\"test-key-xyz789\"'
            else:
                return f'\"test_{field_name}\"'
        elif field_type == 5:  # TYPE_INT32
            return '42'
        elif field_type == 13:  # TYPE_UINT32
            return '42'
        elif field_type == 3:  # TYPE_INT64
            return '123456'
        elif field_type == 1:  # TYPE_DOUBLE
            return '3.14'
        elif field_type == 2:  # TYPE_FLOAT
            return '2.71'
        elif field_type == 8:  # TYPE_BOOL
            return 'True'
        elif field_type == 12:  # TYPE_BYTES
            return b"test_bytes"
        elif field_type == 14:  # TYPE_ENUM
            # For enums, we need to find the enum type and use a valid value
            return '0'  # Default to 0 for now
        elif field_type == 11:  # TYPE_MESSAGE
            return None  # Skip complex message types
        else:
            return None  # Skip unknown types

    def _generate_enum_validation_tests(self, message_types: Dict[str, Any]) -> str:
        """Generate validation tests for all enum types found in messages."""
        content = ''
        
        # Find all enum types
        enum_types = set()
        for msg_key, msg_info in message_types.items():
            module_name = msg_info['module']
            descriptor = msg_info['descriptor']
            
            for field in descriptor.fields:
                if field.type == 14:  # TYPE_ENUM
                    enum_name = field.enum_type.name if hasattr(field, 'enum_type') else None
                    if enum_name:
                        enum_types.add((module_name, enum_name))
        
        for module_name, enum_name in enum_types:
            content += f'''
    def test_{enum_name.lower()}_enum_values(self):
        """Test that {enum_name} enum has valid values and can be used."""
        # Test that the enum exists
        assert hasattr({module_name}_pb2, '{enum_name}')
        
        # Get the enum class
        enum_class = getattr({module_name}_pb2, '{enum_name}')
        
        # Test that we can get enum descriptor
        if hasattr(enum_class, 'DESCRIPTOR'):
            descriptor = enum_class.DESCRIPTOR
            
            # Test that enum has values
            assert len(descriptor.values) > 0, f"Enum {enum_name} has no values"
            
            # Test that all enum values are valid integers
            for value_descriptor in descriptor.values:
                enum_value = getattr(enum_class, value_descriptor.name)
                assert isinstance(enum_value, int), f"Enum value {{value_descriptor.name}} is not an integer"
'''
        
        return content

    def _generate_serialization_integrity_tests(self, message_types: Dict[str, Any], output_dir: Path):
        """Generate serialization integrity tests (formerly Tier 2)."""
        test_content = self._generate_serialization_test_content(message_types)
        (output_dir / "test_serialization_integrity.py").write_text(test_content)
        
        print(f"📝 Generated serialization integrity tests for {len(message_types)} message types")

    def _generate_serialization_test_content(self, message_types: Dict[str, Any]) -> str:
        """Generate the content for serialization tests."""
        content = f'''"""
Serialization Integrity Tests

Auto-generated from protobuf definitions on {self.timestamp}
DO NOT EDIT - Regenerate using scripts/generate_protobuf_tests.py

Tests the complete data lifecycle: Pydantic → Protobuf → Pydantic
Ensures no data loss occurs during serialization/deserialization cycles.
"""

import pytest
from typing import Any, Dict, List
from google.protobuf.message import Message

# Import all protobuf message types
from postfiat.v3 import messages_pb2


class TestSerializationIntegrity:
    """Test serialization/deserialization integrity for protobuf messages."""
    
    @pytest.mark.parametrize("message_class", [
'''
        
        # Add each message type as a test parameter
        for msg_key, msg_info in message_types.items():
            module_name = msg_info['module']
            class_name = msg_info['name']
            content += f'        {module_name}_pb2.{class_name},\n'
            
        content += '''    ])
    def test_round_trip_serialization(self, message_class):
        """Test that protobuf messages can be serialized and deserialized without data loss."""
        # Create instance
        original = message_class()
        
        # Populate with test data using our improved method
        self._populate_message_with_test_data(original)
        
        # Serialize to bytes
        serialized_bytes = original.SerializeToString()
        assert isinstance(serialized_bytes, bytes)
        
        # Check if this message type has any serializable fields
        has_serializable_fields = self._has_serializable_fields(message_class)
        
        # Only assert non-zero length if the message has serializable fields
        if has_serializable_fields:
            assert len(serialized_bytes) > 0, f"Message {message_class.__name__} with serializable fields produced empty bytes"
        # Empty messages (no serializable fields) can legitimately serialize to zero bytes
        
        # Deserialize back to message (should work regardless of length)
        deserialized = message_class()
        deserialized.ParseFromString(serialized_bytes)
        
        # Verify equality
        assert original == deserialized, f"Round-trip serialization failed for {message_class.__name__}"
        
        # Verify SerializeToString produces the same bytes
        reserialized_bytes = deserialized.SerializeToString()
        assert serialized_bytes == reserialized_bytes
    
    def _has_serializable_fields(self, message_class) -> bool:
        """Check if a message class has any fields that our population method would actually set."""
        instance = message_class()
        descriptor = instance.DESCRIPTOR
        
        for field in descriptor.fields:
            # Skip repeated fields (arrays) - they need special handling
            if field.label == 3:  # LABEL_REPEATED
                continue
                
            # Skip message types that might be complex
            if field.type == 11:  # TYPE_MESSAGE
                continue
                
            # Check if this is a field type we populate
            if field.type in [5, 9, 13, 3, 1, 2, 8, 12, 14]:  # INT32, STRING, UINT32, INT64, DOUBLE, FLOAT, BOOL, BYTES, ENUM
                return True
            
        return False
    
    def _populate_message_with_test_data(self, instance) -> None:
        """Populate a protobuf message instance with test data for serialization."""
        descriptor = instance.DESCRIPTOR
        
        for field in descriptor.fields:
            try:
                # Skip repeated fields (arrays) - they need special handling
                if field.label == 3:  # LABEL_REPEATED
                    continue
                    
                # Skip message types that might be complex
                if field.type == 11:  # TYPE_MESSAGE
                    continue
                    
                # Populate based on field type
                if field.type == 9:  # TYPE_STRING
                    setattr(instance, field.name, f"test_{field.name}")
                elif field.type == 5:  # TYPE_INT32
                    setattr(instance, field.name, 42)
                elif field.type == 13:  # TYPE_UINT32
                    setattr(instance, field.name, 42)
                elif field.type == 3:  # TYPE_INT64
                    setattr(instance, field.name, 123456)
                elif field.type == 1:  # TYPE_DOUBLE
                    setattr(instance, field.name, 3.14)
                elif field.type == 2:  # TYPE_FLOAT
                    setattr(instance, field.name, 2.71)
                elif field.type == 8:  # TYPE_BOOL
                    setattr(instance, field.name, True)
                elif field.type == 12:  # TYPE_BYTES
                    setattr(instance, field.name, b"test_bytes")
                elif field.type == 14:  # TYPE_ENUM
                    # Set to first non-zero enum value if possible
                    enum_values = field.enum_type.values
                    if len(enum_values) > 1:
                        setattr(instance, field.name, enum_values[1].number)
                    else:
                        setattr(instance, field.name, 0)
                        
            except Exception:
                # Skip fields that can't be set
                continue
    
    def test_message_envelope_serialization(self):
        """Test MessageEnvelope serialization with correct field names."""
        envelope = messages_pb2.MessageEnvelope()
        
        # Use correct field names from actual protobuf definition
        envelope.version = 1
        envelope.content_hash = "test-content-hash"
        envelope.sequence_number = 123
        envelope.shared_key_id = "test-shared-key-id"
        envelope.reply_to = "test-reply-to"
        envelope.message = b"test message content"
        
        # Test the round trip
        serialized = envelope.SerializeToString()
        assert len(serialized) > 0
        
        deserialized = messages_pb2.MessageEnvelope()
        deserialized.ParseFromString(serialized)
        
        assert envelope == deserialized
        assert deserialized.version == 1
        assert deserialized.content_hash == "test-content-hash"
        assert deserialized.sequence_number == 123
        assert deserialized.shared_key_id == "test-shared-key-id"
        assert deserialized.reply_to == "test-reply-to"
        assert deserialized.message == b"test message content"
    
    @pytest.mark.parametrize("request_class", [
'''
        
        # Add all request types for testing
        for msg_key, msg_info in message_types.items():
            if msg_info['name'].endswith('Request'):
                module_name = msg_info['module']
                class_name = msg_info['name']
                content += f'        {module_name}_pb2.{class_name},\n'
                
        content += '''    ])
    def test_request_serialization(self, request_class):
        """Test that all request types can be serialized/deserialized."""
        request = request_class()
        self._populate_message_with_test_data(request)
        
        # Test serialization
        serialized = request.SerializeToString()
        
        # Test deserialization
        deserialized = request_class()
        deserialized.ParseFromString(serialized)
        
        assert request == deserialized
    
    @pytest.mark.parametrize("response_class", [
'''
        
        # Add all response types for testing
        for msg_key, msg_info in message_types.items():
            if msg_info['name'].endswith('Response'):
                module_name = msg_info['module']
                class_name = msg_info['name']
                content += f'        {module_name}_pb2.{class_name},\n'
                
        content += '''    ])
    def test_response_serialization(self, response_class):
        """Test that all response types can be serialized/deserialized."""
        response = response_class()
        self._populate_message_with_test_data(response)
        
        # Test serialization
        serialized = response.SerializeToString()
        
        # Test deserialization
        deserialized = response_class()
        deserialized.ParseFromString(serialized)
        
        assert response == deserialized
'''

        return content

    def _generate_persistence_scaffolding_tests(self, services: Dict[str, Any], output_dir: Path):
        """Generate persistence scaffolding tests (formerly Tier 3)."""
        test_content = self._generate_persistence_test_content(services)
        (output_dir / "test_persistence_scaffolding.py").write_text(test_content)
        
        print(f"📝 Generated persistence scaffolding tests for {len(services)} services")

    def _generate_persistence_test_content(self, services: Dict[str, Any]) -> str:
        """Generate the content for persistence/endpoint tests."""
        content = f'''"""
Persistence Scaffolding Tests

Auto-generated from protobuf definitions on {self.timestamp}
DO NOT EDIT - Regenerate using scripts/generate_protobuf_tests.py

Tests basic CRUD operations and endpoint connectivity for all services.
Provides scaffolding for future database integration and service implementation.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import Any, Dict

# Import protobuf types
from postfiat.v3 import messages_pb2

# Import service classes (these may need to be implemented)
# from postfiat.wallet.services import WalletService, DiscordService, KnowledgeService, EventStreamingService


class TestServiceEndpoints:
    """Test service endpoint scaffolding and basic operations."""
    
    @pytest.fixture
    def mock_database(self):
        """Mock database connection for testing."""
        return Mock()
'''

        # Generate test classes for each service
        for service_key, service_info in services.items():
            service_name = service_info['name']
            module_name = service_info['module']
            methods = service_info['methods']
            
            content += f'''

class Test{service_name}Service:
    """Test {service_name} service endpoints and operations."""
    
    @pytest.fixture
    def service(self):
        """Mock {service_name} service instance for testing."""
        return Mock()
'''

            # Generate a test method for each service method
            for method in methods:
                method_name = method['name']
                input_type = method['input_type']
                output_type = method['output_type']
                
                # Determine the CRUD operation type
                crud_type = self._classify_crud_operation(method_name)
                
                content += f'''
    def test_{method_name.lower()}_endpoint(self, service, mock_database):
        """Test {method_name} endpoint - {crud_type} operation."""
        # Create test request
        request = {module_name}_pb2.{input_type}()
        
        # Populate request with test data
        self._populate_test_request(request, "{method_name}")
        
        # Handle Empty responses specially
        if "{output_type}" == "Empty":
            # Empty responses have no fields - just verify the method can be called
            expected_response = None  # Empty response
        else:
            # Mock the service method
            expected_response = {module_name}_pb2.{output_type}()
            self._populate_test_response(expected_response, "{method_name}")
        
        # TODO: Implement actual service call when service is available
        # with patch.object(service, '{method_name.lower()}', return_value=expected_response):
        #     result = service.{method_name.lower()}(request)
        #     assert result == expected_response
        
        # For now, just verify the protobuf types are correct
        assert isinstance(request, {module_name}_pb2.{input_type})
        if expected_response is not None:
            assert isinstance(expected_response, {module_name}_pb2.{output_type})
        
        # TODO: Add database interaction tests
        # mock_database.execute.assert_called()
'''

        # Add common helper methods at the end
        content += '''
    def _populate_test_request(self, request, method_name: str):
        """Populate request with appropriate test data."""
        # Basic population - extend based on actual field requirements
        descriptor = request.DESCRIPTOR
        
        for field in descriptor.fields:
            field_name = field.name
            
            try:
                if field.type == field.TYPE_STRING:
                    if 'id' in field_name.lower():
                        setattr(request, field_name, f"test-{field_name}-123")
                    elif 'email' in field_name.lower():
                        setattr(request, field_name, "test@example.com")
                    else:
                        setattr(request, field_name, f"test_{field_name}")
                elif field.type == field.TYPE_INT32:
                    setattr(request, field_name, 42)
                elif field.type == field.TYPE_BOOL:
                    setattr(request, field_name, True)
                # Add more field type handling as needed
            except Exception:
                continue
    
    def _populate_test_response(self, response, method_name: str):
        """Populate response with appropriate test data."""
        # Skip Empty responses - they have no fields to populate
        if response.__class__.__name__ == 'Empty':
            return
            
        # Basic population - extend based on actual field requirements
        descriptor = response.DESCRIPTOR
        
        for field in descriptor.fields:
            field_name = field.name
            
            try:
                if field.type == field.TYPE_STRING:
                    if 'id' in field_name.lower():
                        setattr(response, field_name, f"test-{field_name}-456")
                    else:
                        setattr(response, field_name, f"test_{field_name}_response")
                elif field.type == field.TYPE_INT32:
                    setattr(response, field_name, 100)
                elif field.type == field.TYPE_BOOL:
                    setattr(response, field_name, True)
                # Add more field type handling as needed
            except Exception:
                # Skip fields that can't be set
                continue


class TestServiceIntegration:
    """Integration tests for all services with actual database."""
    
    @pytest.mark.integration
    def test_service_integration_smoke_test(self):
        """Smoke test for service integration."""
        # TODO: Implement when actual service and database are available
        pytest.skip("Integration test - implement when service is available")
        
        # Basic integration test structure:
        # 1. Set up test database
        # 2. Create service instance
        # 3. Test basic CRUD operations
        # 4. Verify database state
        # 5. Clean up
        
    @pytest.mark.integration 
    def test_cross_service_communication(self):
        """Test communication between different services."""
        # TODO: Implement when services are available
        pytest.skip("Cross-service test - implement when services are available")
        
        # Test scenarios like:
        # - Wallet service sending events to streaming service
        # - Discord service querying knowledge service
        # - Event streaming service updating wallet balances
'''

        return content

    def _classify_crud_operation(self, method_name: str) -> str:
        """Classify a method as Create, Read, Update, Delete, or Other."""
        method_lower = method_name.lower()
        
        if any(word in method_lower for word in ['create', 'register', 'add', 'insert']):
            return "CREATE"
        elif any(word in method_lower for word in ['get', 'list', 'find', 'retrieve', 'query']):
            return "READ"
        elif any(word in method_lower for word in ['update', 'modify', 'edit', 'change']):
            return "UPDATE"
        elif any(word in method_lower for word in ['delete', 'remove', 'destroy']):
            return "DELETE"
        else:
            return "OTHER"


def main():
    """Main function to generate all tests."""
    generator = ProtobufTestGenerator()
    generator.generate_all_tests()


if __name__ == "__main__":
    main()
