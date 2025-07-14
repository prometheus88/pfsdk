#!/usr/bin/env python3
"""
PostFiat SDK: A2A Integration Example

This example demonstrates how to use PostFiat selective disclosure
envelopes within A2A gRPC messages.

Setup:
1. Run: ./scripts/setup-a2a-dependency.sh
2. Generate code: cd proto && buf generate
3. Run this example: python examples/a2a_integration_example.py

PostFiat extends A2A gRPC with selective disclosure capabilities.
PostFiat envelopes are embedded in A2A Message.content as DataPart structures.
"""

# Import A2A types
from a2a.v1.a2a_pb2 import (
    Message, Part, DataPart, Role,
    AgentCapabilities, AgentExtension
)

# Import PostFiat types
from postfiat.v3.messages_pb2 import (
    Envelope, CoreMessage,
    PostFiatEnvelopePayload,
    EncryptionMode, MessageType
)

from google.protobuf.struct_pb2 import Struct


def create_postfiat_agent_capabilities() -> AgentCapabilities:
    """Create A2A AgentCapabilities with PostFiat extension."""
    
    # Extension parameters
    extension_params = Struct()
    extension_params.update({
        "max_context_depth": 10,
        "supported_encryption_modes": ["PROTECTED", "PUBLIC_KEY", "NONE"],
        "ledger_persistence": True
    })
    
    # A2A AgentCapabilities with PostFiat extension
    capabilities = AgentCapabilities(
        streaming=True,
        push_notifications=True,
        extensions=[
            AgentExtension(
                uri="https://postfiat.org/extensions/envelope/v1",
                description="PostFiat selective disclosure and ledger persistence",
                required=False,
                params=extension_params
            )
        ]
    )
    
    return capabilities


def create_postfiat_envelope_message(
    content: str,
    context_references: list = None,
    encryption_mode: EncryptionMode = EncryptionMode.PROTECTED
) -> PostFiatEnvelopePayload:
    """Create a PostFiat envelope payload for A2A message with automatic chunking."""
    from postfiat.envelope import EnvelopeFactory
    
    # Create envelope factory with 1000 byte limit
    envelope_factory = EnvelopeFactory(max_envelope_size=1000)
    
    # Create envelope(s) - will automatically chunk if content is too large
    envelope_result = envelope_factory.create_envelope(
        content=content,
        context_references=context_references,
        encryption_mode=encryption_mode
    )
    
    # Handle single envelope vs chunked envelopes
    if isinstance(envelope_result, Envelope):
        # Single envelope - fits within size limit
        envelope = envelope_result
    else:
        # Multiple envelopes - content was chunked
        # For A2A integration, we'll use the first chunk as primary envelope
        # and include metadata about the chunking
        envelopes = list(envelope_result)
        envelope = envelopes[0]  # Primary envelope
        
        # Add chunking metadata to indicate this is part of a multipart message
        if "chunk_info" not in envelope.metadata:
            envelope.metadata["multipart_message"] = "true"
            envelope.metadata["total_chunks"] = str(len(envelopes))
    
    # Create PostFiat envelope payload
    payload = PostFiatEnvelopePayload(
        envelope=envelope,
        content_address="content_addr_placeholder",  # Content-addressable hash
        postfiat_metadata={
            "extension_version": "v1",
            "processing_mode": "selective_disclosure"
        }
    )
    
    return payload


def create_a2a_message_with_postfiat(
    message_id: str,
    context_id: str,
    content: str,
    role: Role = Role.ROLE_USER
) -> Message:
    """Create an A2A Message with PostFiat envelope payload."""
    
    # Create PostFiat envelope payload
    postfiat_payload = create_postfiat_envelope_message(content)
    
    # Convert to Struct for DataPart
    payload_struct = Struct()
    payload_struct.update({
        "postfiat_envelope": {
            "envelope": {
                "version": postfiat_payload.envelope.version,
                "content_hash": postfiat_payload.envelope.content_hash,
                "message_type": postfiat_payload.envelope.message_type,
                "encryption": postfiat_payload.envelope.encryption,
                "message": postfiat_payload.envelope.message.hex(),  # Hex encode bytes
                "metadata": dict(postfiat_payload.envelope.metadata)
            },
            "content_address": postfiat_payload.content_address,
            "postfiat_metadata": dict(postfiat_payload.postfiat_metadata)
        }
    })
    
    # Create A2A Message with PostFiat extension
    message = Message(
        message_id=message_id,
        context_id=context_id,
        role=role,
        content=[
            Part(data=DataPart(data=payload_struct))
        ],
        extensions=["https://postfiat.org/extensions/envelope/v1"]
    )
    
    return message


def main():
    """Demonstrate A2A + PostFiat integration."""
    
    print("🔧 PostFiat SDK: A2A Integration Example")
    print("=" * 50)
    
    # 1. Create PostFiat agent capabilities
    print("\n1. Creating PostFiat agent capabilities...")
    capabilities = create_postfiat_agent_capabilities()
    print(f"   Extensions: {[ext.uri for ext in capabilities.extensions]}")
    
    # 2. Create A2A message with PostFiat envelope
    print("\n2. Creating A2A message with PostFiat envelope...")
    message = create_a2a_message_with_postfiat(
        message_id="msg_12345",
        context_id="ai_research_2024",
        content="What are the latest developments in AI ethics research?",
        role=Role.ROLE_USER
    )
    
    print(f"   Message ID: {message.message_id}")
    print(f"   Context ID: {message.context_id}")
    print(f"   Extensions: {message.extensions}")
    print(f"   Content parts: {len(message.content)}")
    
    # 3. Demonstrate envelope extraction
    print("\n3. Extracting PostFiat envelope from A2A message...")
    if message.content and message.content[0].HasField('data'):
        data_struct = message.content[0].data.data
        if 'postfiat_envelope' in data_struct:
            envelope_data = data_struct['postfiat_envelope']
            print(f"   Envelope version: {envelope_data['envelope']['version']}")
            print(f"   Content address: {envelope_data['content_address']}")
            print(f"   Encryption mode: {envelope_data['envelope']['encryption']}")
    
    print("\n✅ A2A + PostFiat integration example complete!")
    print("\nNext steps:")
    print("- Implement A2A gRPC service with PostFiat envelope processing")
    print("- Add XRPL ledger persistence for audit trails")
    print("- Build context DAG traversal for selective disclosure")


if __name__ == "__main__":
    main()
