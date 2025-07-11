"""Auto-generated SQLModel database models from protobuf definitions.

DO NOT EDIT - This file is auto-generated from proto files.
Run 'python scripts/generate_python_types.py' to regenerate.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from pydantic import ConfigDict
import json


class AccessGrant(SQLModel, table=True):
    """SQLModel for AccessGrant protobuf message."""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = Field(default=None, primary_key=True)
    key_type: Optional[int] = Field(default=None)
    target_id: Optional[str] = Field(default=None)
    encrypted_key_material: Optional[bytes] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    @classmethod
    def from_protobuf(cls, pb_message) -> "AccessGrant":
        """Create SQLModel instance from protobuf message."""
        from postfiat.logging import get_logger
        logger = get_logger("models.accessgrant")

        data = {}
        if hasattr(pb_message, "key_type"):
            data["key_type"] = pb_message.key_type
        if hasattr(pb_message, "target_id"):
            data["target_id"] = pb_message.target_id
        if hasattr(pb_message, "encrypted_key_material"):
            data["encrypted_key_material"] = pb_message.encrypted_key_material

        logger.debug(
            "Converting protobuf to SQLModel",
            message_type="AccessGrant",
            field_count=len(data)
        )

        return cls(**data)

    def to_protobuf(self):
        """Convert SQLModel instance to protobuf message."""
        from postfiat.v3 import messages_pb2, errors_pb2
        from postfiat.logging import get_logger
        logger = get_logger("models.accessgrant")

        pb_message = messages_pb2.AccessGrant()
        if self.key_type is not None:
            pb_message.key_type = self.key_type
        if self.target_id is not None:
            pb_message.target_id = self.target_id
        if self.encrypted_key_material is not None:
            pb_message.encrypted_key_material = self.encrypted_key_material

        logger.debug(
            "Converting SQLModel to protobuf",
            message_type="AccessGrant",
            model_id=self.id
        )

        return pb_message


class ContextReference(SQLModel, table=True):
    """SQLModel for ContextReference protobuf message."""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = Field(default=None, primary_key=True)
    content_hash: Optional[bytes] = Field(default=None)
    group_id: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    @classmethod
    def from_protobuf(cls, pb_message) -> "ContextReference":
        """Create SQLModel instance from protobuf message."""
        from postfiat.logging import get_logger
        logger = get_logger("models.contextreference")

        data = {}
        if hasattr(pb_message, "content_hash"):
            data["content_hash"] = pb_message.content_hash
        if hasattr(pb_message, "group_id"):
            data["group_id"] = pb_message.group_id

        logger.debug(
            "Converting protobuf to SQLModel",
            message_type="ContextReference",
            field_count=len(data)
        )

        return cls(**data)

    def to_protobuf(self):
        """Convert SQLModel instance to protobuf message."""
        from postfiat.v3 import messages_pb2, errors_pb2
        from postfiat.logging import get_logger
        logger = get_logger("models.contextreference")

        pb_message = messages_pb2.ContextReference()
        if self.content_hash is not None:
            pb_message.content_hash = self.content_hash
        if self.group_id is not None:
            pb_message.group_id = self.group_id

        logger.debug(
            "Converting SQLModel to protobuf",
            message_type="ContextReference",
            model_id=self.id
        )

        return pb_message


class CoreMessage(SQLModel, table=True):
    """SQLModel for CoreMessage protobuf message."""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = Field(default=None, primary_key=True)
    content: Optional[str] = Field(default=None)
    context_references: Optional[str] = Field(default=None, description="JSON-encoded list of context_references")
    message_metadata: Optional[str] = Field(default=None, description="JSON-encoded message_metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    @classmethod
    def from_protobuf(cls, pb_message) -> "CoreMessage":
        """Create SQLModel instance from protobuf message."""
        from postfiat.logging import get_logger
        logger = get_logger("models.coremessage")

        data = {}
        if hasattr(pb_message, "content"):
            data["content"] = pb_message.content
        if hasattr(pb_message, "context_references"):
            data["context_references"] = json.dumps(list(pb_message.context_references))
        if hasattr(pb_message, "metadata"):
            data["message_metadata"] = json.dumps(dict(pb_message.metadata))

        logger.debug(
            "Converting protobuf to SQLModel",
            message_type="CoreMessage",
            field_count=len(data)
        )

        return cls(**data)

    def to_protobuf(self):
        """Convert SQLModel instance to protobuf message."""
        from postfiat.v3 import messages_pb2, errors_pb2
        from postfiat.logging import get_logger
        logger = get_logger("models.coremessage")

        pb_message = messages_pb2.CoreMessage()
        if self.content is not None:
            pb_message.content = self.content
        if self.context_references is not None:
            items = json.loads(self.context_references)
            pb_message.context_references.extend(items)
        if self.message_metadata is not None:
            metadata_dict = json.loads(self.message_metadata)
            pb_message.metadata.update(metadata_dict)

        logger.debug(
            "Converting SQLModel to protobuf",
            message_type="CoreMessage",
            model_id=self.id
        )

        return pb_message


class Envelope(SQLModel, table=True):
    """SQLModel for Envelope protobuf message."""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = Field(default=None, primary_key=True)
    version: Optional[int] = Field(default=None)
    content_hash: Optional[bytes] = Field(default=None)
    message_type: Optional[int] = Field(default=None)
    encryption: Optional[int] = Field(default=None)
    reply_to: Optional[str] = Field(default=None)
    public_references: Optional[str] = Field(default=None, description="JSON-encoded list of public_references")
    access_grants: Optional[str] = Field(default=None, description="JSON-encoded list of access_grants")
    message: Optional[bytes] = Field(default=None)
    message_metadata: Optional[str] = Field(default=None, description="JSON-encoded message_metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    @classmethod
    def from_protobuf(cls, pb_message) -> "Envelope":
        """Create SQLModel instance from protobuf message."""
        from postfiat.logging import get_logger
        logger = get_logger("models.envelope")

        data = {}
        if hasattr(pb_message, "version"):
            data["version"] = pb_message.version
        if hasattr(pb_message, "content_hash"):
            data["content_hash"] = pb_message.content_hash
        if hasattr(pb_message, "message_type"):
            data["message_type"] = pb_message.message_type
        if hasattr(pb_message, "encryption"):
            data["encryption"] = pb_message.encryption
        if hasattr(pb_message, "reply_to"):
            data["reply_to"] = pb_message.reply_to
        if hasattr(pb_message, "public_references"):
            data["public_references"] = json.dumps(list(pb_message.public_references))
        if hasattr(pb_message, "access_grants"):
            data["access_grants"] = json.dumps(list(pb_message.access_grants))
        if hasattr(pb_message, "message"):
            data["message"] = pb_message.message
        if hasattr(pb_message, "metadata"):
            data["message_metadata"] = json.dumps(dict(pb_message.metadata))

        logger.debug(
            "Converting protobuf to SQLModel",
            message_type="Envelope",
            field_count=len(data)
        )

        return cls(**data)

    def to_protobuf(self):
        """Convert SQLModel instance to protobuf message."""
        from postfiat.v3 import messages_pb2, errors_pb2
        from postfiat.logging import get_logger
        logger = get_logger("models.envelope")

        pb_message = messages_pb2.Envelope()
        if self.version is not None:
            pb_message.version = self.version
        if self.content_hash is not None:
            pb_message.content_hash = self.content_hash
        if self.message_type is not None:
            pb_message.message_type = self.message_type
        if self.encryption is not None:
            pb_message.encryption = self.encryption
        if self.reply_to is not None:
            pb_message.reply_to = self.reply_to
        if self.public_references is not None:
            items = json.loads(self.public_references)
            pb_message.public_references.extend(items)
        if self.access_grants is not None:
            items = json.loads(self.access_grants)
            pb_message.access_grants.extend(items)
        if self.message is not None:
            pb_message.message = self.message
        if self.message_metadata is not None:
            metadata_dict = json.loads(self.message_metadata)
            pb_message.metadata.update(metadata_dict)

        logger.debug(
            "Converting SQLModel to protobuf",
            message_type="Envelope",
            model_id=self.id
        )

        return pb_message


class MultiPartMessagePart(SQLModel, table=True):
    """SQLModel for MultiPartMessagePart protobuf message."""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = Field(default=None, primary_key=True)
    message_id: Optional[str] = Field(default=None)
    part_number: Optional[int] = Field(default=None)
    total_parts: Optional[int] = Field(default=None)
    content: Optional[bytes] = Field(default=None)
    complete_message_hash: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    @classmethod
    def from_protobuf(cls, pb_message) -> "MultiPartMessagePart":
        """Create SQLModel instance from protobuf message."""
        from postfiat.logging import get_logger
        logger = get_logger("models.multipartmessagepart")

        data = {}
        if hasattr(pb_message, "message_id"):
            data["message_id"] = pb_message.message_id
        if hasattr(pb_message, "part_number"):
            data["part_number"] = pb_message.part_number
        if hasattr(pb_message, "total_parts"):
            data["total_parts"] = pb_message.total_parts
        if hasattr(pb_message, "content"):
            data["content"] = pb_message.content
        if hasattr(pb_message, "complete_message_hash"):
            data["complete_message_hash"] = pb_message.complete_message_hash

        logger.debug(
            "Converting protobuf to SQLModel",
            message_type="MultiPartMessagePart",
            field_count=len(data)
        )

        return cls(**data)

    def to_protobuf(self):
        """Convert SQLModel instance to protobuf message."""
        from postfiat.v3 import messages_pb2, errors_pb2
        from postfiat.logging import get_logger
        logger = get_logger("models.multipartmessagepart")

        pb_message = messages_pb2.MultiPartMessagePart()
        if self.message_id is not None:
            pb_message.message_id = self.message_id
        if self.part_number is not None:
            pb_message.part_number = self.part_number
        if self.total_parts is not None:
            pb_message.total_parts = self.total_parts
        if self.content is not None:
            pb_message.content = self.content
        if self.complete_message_hash is not None:
            pb_message.complete_message_hash = self.complete_message_hash

        logger.debug(
            "Converting SQLModel to protobuf",
            message_type="MultiPartMessagePart",
            model_id=self.id
        )

        return pb_message


class PostFiatA2AMessage(SQLModel, table=True):
    """SQLModel for PostFiatA2AMessage protobuf message."""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = Field(default=None, primary_key=True)
    a2a_message: Optional[str] = Field(default=None)
    postfiat_payload: Optional[str] = Field(default=None)
    integration_metadata: Optional[str] = Field(default=None, description="JSON-encoded list of integration_metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    @classmethod
    def from_protobuf(cls, pb_message) -> "PostFiatA2AMessage":
        """Create SQLModel instance from protobuf message."""
        from postfiat.logging import get_logger
        logger = get_logger("models.postfiata2amessage")

        data = {}
        if hasattr(pb_message, "a2a_message"):
            data["a2a_message"] = pb_message.a2a_message
        if hasattr(pb_message, "postfiat_payload"):
            data["postfiat_payload"] = pb_message.postfiat_payload
        if hasattr(pb_message, "integration_metadata"):
            data["integration_metadata"] = json.dumps(list(pb_message.integration_metadata))

        logger.debug(
            "Converting protobuf to SQLModel",
            message_type="PostFiatA2AMessage",
            field_count=len(data)
        )

        return cls(**data)

    def to_protobuf(self):
        """Convert SQLModel instance to protobuf message."""
        from postfiat.v3 import messages_pb2, errors_pb2
        from postfiat.logging import get_logger
        logger = get_logger("models.postfiata2amessage")

        pb_message = messages_pb2.PostFiatA2AMessage()
        if self.a2a_message is not None:
            pb_message.a2a_message = self.a2a_message
        if self.postfiat_payload is not None:
            pb_message.postfiat_payload = self.postfiat_payload
        if self.integration_metadata is not None:
            items = json.loads(self.integration_metadata)
            pb_message.integration_metadata.extend(items)

        logger.debug(
            "Converting SQLModel to protobuf",
            message_type="PostFiatA2AMessage",
            model_id=self.id
        )

        return pb_message


class PostFiatAgentCapabilities(SQLModel, table=True):
    """SQLModel for PostFiatAgentCapabilities protobuf message."""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = Field(default=None, primary_key=True)
    envelope_processing: Optional[bool] = Field(default=None)
    ledger_persistence: Optional[bool] = Field(default=None)
    context_dag_traversal: Optional[bool] = Field(default=None)
    max_context_depth: Optional[int] = Field(default=None)
    supported_encryption_modes: Optional[str] = Field(default=None, description="JSON-encoded list of supported_encryption_modes")
    public_encryption_key: Optional[bytes] = Field(default=None)
    public_key_algorithm: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    @classmethod
    def from_protobuf(cls, pb_message) -> "PostFiatAgentCapabilities":
        """Create SQLModel instance from protobuf message."""
        from postfiat.logging import get_logger
        logger = get_logger("models.postfiatagentcapabilities")

        data = {}
        if hasattr(pb_message, "envelope_processing"):
            data["envelope_processing"] = pb_message.envelope_processing
        if hasattr(pb_message, "ledger_persistence"):
            data["ledger_persistence"] = pb_message.ledger_persistence
        if hasattr(pb_message, "context_dag_traversal"):
            data["context_dag_traversal"] = pb_message.context_dag_traversal
        if hasattr(pb_message, "max_context_depth"):
            data["max_context_depth"] = pb_message.max_context_depth
        if hasattr(pb_message, "supported_encryption_modes"):
            data["supported_encryption_modes"] = json.dumps(list(pb_message.supported_encryption_modes))
        if hasattr(pb_message, "public_encryption_key"):
            data["public_encryption_key"] = pb_message.public_encryption_key
        if hasattr(pb_message, "public_key_algorithm"):
            data["public_key_algorithm"] = pb_message.public_key_algorithm

        logger.debug(
            "Converting protobuf to SQLModel",
            message_type="PostFiatAgentCapabilities",
            field_count=len(data)
        )

        return cls(**data)

    def to_protobuf(self):
        """Convert SQLModel instance to protobuf message."""
        from postfiat.v3 import messages_pb2, errors_pb2
        from postfiat.logging import get_logger
        logger = get_logger("models.postfiatagentcapabilities")

        pb_message = messages_pb2.PostFiatAgentCapabilities()
        if self.envelope_processing is not None:
            pb_message.envelope_processing = self.envelope_processing
        if self.ledger_persistence is not None:
            pb_message.ledger_persistence = self.ledger_persistence
        if self.context_dag_traversal is not None:
            pb_message.context_dag_traversal = self.context_dag_traversal
        if self.max_context_depth is not None:
            pb_message.max_context_depth = self.max_context_depth
        if self.supported_encryption_modes is not None:
            items = json.loads(self.supported_encryption_modes)
            pb_message.supported_encryption_modes.extend(items)
        if self.public_encryption_key is not None:
            pb_message.public_encryption_key = self.public_encryption_key
        if self.public_key_algorithm is not None:
            pb_message.public_key_algorithm = self.public_key_algorithm

        logger.debug(
            "Converting SQLModel to protobuf",
            message_type="PostFiatAgentCapabilities",
            model_id=self.id
        )

        return pb_message


class PostFiatEnvelopePayload(SQLModel, table=True):
    """SQLModel for PostFiatEnvelopePayload protobuf message."""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = Field(default=None, primary_key=True)
    envelope: Optional[str] = Field(default=None)
    xrpl_transaction_hash: Optional[str] = Field(default=None)
    content_address: Optional[str] = Field(default=None)
    postfiat_metadata: Optional[str] = Field(default=None, description="JSON-encoded list of postfiat_metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    @classmethod
    def from_protobuf(cls, pb_message) -> "PostFiatEnvelopePayload":
        """Create SQLModel instance from protobuf message."""
        from postfiat.logging import get_logger
        logger = get_logger("models.postfiatenvelopepayload")

        data = {}
        if hasattr(pb_message, "envelope"):
            data["envelope"] = pb_message.envelope
        if hasattr(pb_message, "xrpl_transaction_hash"):
            data["xrpl_transaction_hash"] = pb_message.xrpl_transaction_hash
        if hasattr(pb_message, "content_address"):
            data["content_address"] = pb_message.content_address
        if hasattr(pb_message, "postfiat_metadata"):
            data["postfiat_metadata"] = json.dumps(list(pb_message.postfiat_metadata))

        logger.debug(
            "Converting protobuf to SQLModel",
            message_type="PostFiatEnvelopePayload",
            field_count=len(data)
        )

        return cls(**data)

    def to_protobuf(self):
        """Convert SQLModel instance to protobuf message."""
        from postfiat.v3 import messages_pb2, errors_pb2
        from postfiat.logging import get_logger
        logger = get_logger("models.postfiatenvelopepayload")

        pb_message = messages_pb2.PostFiatEnvelopePayload()
        if self.envelope is not None:
            pb_message.envelope = self.envelope
        if self.xrpl_transaction_hash is not None:
            pb_message.xrpl_transaction_hash = self.xrpl_transaction_hash
        if self.content_address is not None:
            pb_message.content_address = self.content_address
        if self.postfiat_metadata is not None:
            items = json.loads(self.postfiat_metadata)
            pb_message.postfiat_metadata.extend(items)

        logger.debug(
            "Converting SQLModel to protobuf",
            message_type="PostFiatEnvelopePayload",
            model_id=self.id
        )

        return pb_message


class ErrorInfo(SQLModel, table=True):
    """SQLModel for ErrorInfo protobuf message."""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = Field(default=None, primary_key=True)
    code: Optional[int] = Field(default=None)
    category: Optional[int] = Field(default=None)
    severity: Optional[int] = Field(default=None)
    message: Optional[str] = Field(default=None)
    details: Optional[str] = Field(default=None)
    field: Optional[str] = Field(default=None)
    context: Optional[str] = Field(default=None, description="JSON-encoded list of context")
    timestamp: Optional[int] = Field(default=None)
    error_id: Optional[str] = Field(default=None)
    debug_info: Optional[str] = Field(default=None)
    remediation: Optional[str] = Field(default=None, description="JSON-encoded list of remediation")
    related_errors: Optional[str] = Field(default=None, description="JSON-encoded list of related_errors")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    @classmethod
    def from_protobuf(cls, pb_message) -> "ErrorInfo":
        """Create SQLModel instance from protobuf message."""
        from postfiat.logging import get_logger
        logger = get_logger("models.errorinfo")

        data = {}
        if hasattr(pb_message, "code"):
            data["code"] = pb_message.code
        if hasattr(pb_message, "category"):
            data["category"] = pb_message.category
        if hasattr(pb_message, "severity"):
            data["severity"] = pb_message.severity
        if hasattr(pb_message, "message"):
            data["message"] = pb_message.message
        if hasattr(pb_message, "details"):
            data["details"] = pb_message.details
        if hasattr(pb_message, "field"):
            data["field"] = pb_message.field
        if hasattr(pb_message, "context"):
            data["context"] = json.dumps(list(pb_message.context))
        if hasattr(pb_message, "timestamp"):
            data["timestamp"] = pb_message.timestamp
        if hasattr(pb_message, "error_id"):
            data["error_id"] = pb_message.error_id
        if hasattr(pb_message, "debug_info"):
            data["debug_info"] = pb_message.debug_info
        if hasattr(pb_message, "remediation"):
            data["remediation"] = json.dumps(list(pb_message.remediation))
        if hasattr(pb_message, "related_errors"):
            data["related_errors"] = json.dumps(list(pb_message.related_errors))

        logger.debug(
            "Converting protobuf to SQLModel",
            message_type="ErrorInfo",
            field_count=len(data)
        )

        return cls(**data)

    def to_protobuf(self):
        """Convert SQLModel instance to protobuf message."""
        from postfiat.v3 import messages_pb2, errors_pb2
        from postfiat.logging import get_logger
        logger = get_logger("models.errorinfo")

        pb_message = errors_pb2.ErrorInfo()
        if self.code is not None:
            pb_message.code = self.code
        if self.category is not None:
            pb_message.category = self.category
        if self.severity is not None:
            pb_message.severity = self.severity
        if self.message is not None:
            pb_message.message = self.message
        if self.details is not None:
            pb_message.details = self.details
        if self.field is not None:
            pb_message.field = self.field
        if self.context is not None:
            items = json.loads(self.context)
            pb_message.context.extend(items)
        if self.timestamp is not None:
            pb_message.timestamp = self.timestamp
        if self.error_id is not None:
            pb_message.error_id = self.error_id
        if self.debug_info is not None:
            pb_message.debug_info = self.debug_info
        if self.remediation is not None:
            items = json.loads(self.remediation)
            pb_message.remediation.extend(items)
        if self.related_errors is not None:
            items = json.loads(self.related_errors)
            pb_message.related_errors.extend(items)

        logger.debug(
            "Converting SQLModel to protobuf",
            message_type="ErrorInfo",
            model_id=self.id
        )

        return pb_message


class ErrorResponse(SQLModel, table=True):
    """SQLModel for ErrorResponse protobuf message."""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = Field(default=None, primary_key=True)
    error: Optional[str] = Field(default=None)
    additional_errors: Optional[str] = Field(default=None, description="JSON-encoded list of additional_errors")
    request_id: Optional[str] = Field(default=None)
    api_version: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    @classmethod
    def from_protobuf(cls, pb_message) -> "ErrorResponse":
        """Create SQLModel instance from protobuf message."""
        from postfiat.logging import get_logger
        logger = get_logger("models.errorresponse")

        data = {}
        if hasattr(pb_message, "error"):
            data["error"] = pb_message.error
        if hasattr(pb_message, "additional_errors"):
            data["additional_errors"] = json.dumps(list(pb_message.additional_errors))
        if hasattr(pb_message, "request_id"):
            data["request_id"] = pb_message.request_id
        if hasattr(pb_message, "api_version"):
            data["api_version"] = pb_message.api_version

        logger.debug(
            "Converting protobuf to SQLModel",
            message_type="ErrorResponse",
            field_count=len(data)
        )

        return cls(**data)

    def to_protobuf(self):
        """Convert SQLModel instance to protobuf message."""
        from postfiat.v3 import messages_pb2, errors_pb2
        from postfiat.logging import get_logger
        logger = get_logger("models.errorresponse")

        pb_message = errors_pb2.ErrorResponse()
        if self.error is not None:
            pb_message.error = self.error
        if self.additional_errors is not None:
            items = json.loads(self.additional_errors)
            pb_message.additional_errors.extend(items)
        if self.request_id is not None:
            pb_message.request_id = self.request_id
        if self.api_version is not None:
            pb_message.api_version = self.api_version

        logger.debug(
            "Converting SQLModel to protobuf",
            message_type="ErrorResponse",
            model_id=self.id
        )

        return pb_message



# Export all generated models
__all__ = ['AccessGrant', 'ContextReference', 'CoreMessage', 'Envelope', 'MultiPartMessagePart', 'PostFiatA2AMessage', 'PostFiatAgentCapabilities', 'PostFiatEnvelopePayload', 'ErrorInfo', 'ErrorResponse']
