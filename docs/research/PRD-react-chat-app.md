# PostFiat React Chat Application - Product Requirements Document

## Overview

This PRD outlines the requirements for building a React-based chat application that serves as a reference implementation of PostFiat's audit mode communication through XRPL. The application demonstrates how to build cryptographically secure, auditable communications using PostFiat's envelope-based selective disclosure system.

## Executive Summary

The PostFiat React Chat App will be a browser-based demonstration application that showcases:
- **Pure ledger-based communication** using XRPL as the transport layer
- **Selective disclosure** through cryptographic context references
- **Immutable audit trails** for regulatory compliance
- **Modern web UX** that abstracts cryptographic complexity

This serves as both a developer reference and a user-facing demonstration of PostFiat's capabilities.

## Product Vision

Create a chat application that demonstrates how cryptographic messaging can provide both privacy and auditability, solving the fundamental tension between selective disclosure and regulatory compliance through blockchain-based communication.

## Target Audience

### Primary Users
- **Developers** learning PostFiat protocol integration
- **Compliance officers** evaluating audit capabilities
- **Technical decision makers** assessing crypto-communication solutions

### Secondary Users
- **Researchers** studying selective disclosure patterns
- **Regulators** understanding immutable audit trails
- **Open source contributors** extending PostFiat ecosystem

## Core Requirements

### 1. Audit Mode Communication

#### 1.1 Pure Ledger Architecture
- **XRPL as primary transport**: All messages sent as Payment transactions with PostFiat envelopes in memo fields
- **Agent polling pattern**: Continuous monitoring of XRPL for new transactions
- **No real-time servers**: Eliminates infrastructure complexity and points of failure
- **Immutable by design**: Complete conversation history permanently recorded on ledger

#### 1.2 Transaction Processing
- **Memo field encoding**: Serialize PostFiat envelopes into XRPL transaction memos
- **Polling infrastructure**: Monitor user's XRPL address for incoming transactions
- **Transaction filtering**: Identify PostFiat messages vs. regular payments
- **Duplicate handling**: Prevent processing same transaction multiple times

#### 1.3 Cost Management
- **Minimal XRP usage**: Micro-payments for message delivery
- **Fee estimation**: Show cost per message before sending
- **Batch processing**: Group multiple messages when possible
- **Cost reporting**: Track communication expenses

### 2. Cryptographic Message Flow

#### 2.1 Message Envelope Structure
```protobuf
message Envelope {
  uint32 version = 1;                    // Protocol version
  string content_hash = 2;               // Integrity verification
  MessageType message_type = 3;          // CORE_MESSAGE for chat
  EncryptionMode encryption = 4;         // Encryption method
  string reply_to = 5;                   // Message threading
  repeated ContextReference public_references = 6;  // Selective disclosure
  bytes message = 7;                     // Actual chat content
  map<string, string> metadata = 8;     // Routing/filtering metadata
}
```

#### 2.2 Encryption Modes
- **NONE**: Public messages for open disclosure
- **PROTECTED**: Content-addressable encryption with derived keys for group access
- **PUBLIC_KEY**: Traditional public key encryption for direct communication

#### 2.3 Context References
- **Reference creation**: Generate context hashes for message threading
- **Selective disclosure**: Control which references are publicly visible
- **Context DAG**: Build dependency graphs from cryptographic references
- **Access control**: Manage who can decrypt referenced content

### 3. User Interface Requirements

#### 3.1 Chat Interface
- **Message composition**: Rich text input with context reference insertion
- **Conversation threading**: Group messages by context_id
- **Audit mode indicator**: Visual confirmation of ledger-based delivery
- **Encryption status**: Clear indication of message protection level
- **Context visualization**: Show accessible vs. opaque references

#### 3.2 Key Management Dashboard
- **Active projects**: Display collaborations with participant counts
- **Recent activity**: Track shared content and invitations
- **Discovery opportunities**: Suggest relevant collaborators and content
- **Context detail views**: Show accessible content and access management

#### 3.3 Audit Trail View
- **Immutable history**: Display complete conversation record from XRPL
- **Transaction verification**: Show XRPL transaction IDs and confirmations
- **Export functionality**: Generate audit reports for compliance
- **Timeline visualization**: Chronological message flow with ledger timestamps

### 4. Technical Implementation

#### 4.1 XRPL Integration
- **Network connectivity**: Support for mainnet, testnet, and devnet
- **Wallet management**: Secure private key handling for transaction signing
- **Transaction monitoring**: Real-time polling of user's XRPL address
- **Memo processing**: Encode/decode PostFiat envelopes in transaction memos

#### 4.2 PostFiat SDK Integration
- **React hooks**: Utilize `usePostFiatClient()` and `PostFiatProvider`
- **Type safety**: Leverage generated TypeScript types from protobuf definitions
- **Error handling**: Graceful degradation for network or crypto failures
- **Configuration management**: Environment-specific endpoints and settings

#### 4.3 State Management
- **Message persistence**: Local storage of conversation history
- **Real-time updates**: Reflect new messages from ledger polling
- **Context tracking**: Maintain accessible reference relationships
- **Key caching**: Secure local storage of decryption keys

### 5. User Experience Design

#### 5.1 Onboarding Flow
1. **Wallet connection**: Link existing XRPL wallet or create new one
2. **Identity setup**: Configure PostFiat agent identity
3. **Key generation**: Create encryption keys for protected communication
4. **Network selection**: Choose XRPL network (testnet recommended for demo)
5. **Agent discovery**: Find other PostFiat-enabled agents

#### 5.2 Communication Workflow
1. **Agent discovery**: Find contacts through registry or direct ledger verification
2. **Message composition**: Create messages with optional context references
3. **Encryption selection**: Choose protection level (none/protected/public_key)
4. **Audit confirmation**: Verify ledger-based delivery preference
5. **Context sharing**: Grant selective access to conversation history

#### 5.3 Key Management Workflow
1. **Semantic organization**: Group keys by projects and collaborations
2. **Smart discovery**: Search and collaboration pattern analysis
3. **Automated categorization**: AI-powered tagging and metadata extraction
4. **Lifecycle management**: Handle inactive keys and cleanup suggestions

### 6. Security Requirements

#### 6.1 Key Management
- **Client-side encryption**: All cryptographic operations in browser
- **Key derivation**: Deterministic key generation from user credentials
- **Secure storage**: Protected local storage of sensitive materials
- **Key rotation**: Support for updating encryption keys

#### 6.2 Message Security
- **End-to-end encryption**: Messages protected from sender to recipient
- **Integrity verification**: Content hashing prevents tampering
- **Forward secrecy**: Compromised keys don't affect past messages
- **Selective disclosure**: Fine-grained access control for context references

#### 6.3 XRPL Security
- **Transaction signing**: Secure private key operations
- **Network verification**: Validate XRPL node connections
- **Replay protection**: Prevent duplicate transaction processing
- **Rate limiting**: Prevent spam and DoS attacks

### 7. Technical Constraints

#### 7.1 Browser Limitations
- **WebCrypto API**: Utilize browser's native cryptographic primitives
- **Storage limits**: Manage local storage capacity for message history
- **Network restrictions**: Handle CORS and CSP constraints
- **Performance**: Optimize for real-time message processing

#### 7.2 XRPL Constraints
- **Transaction limits**: Maximum memo size (1KB) for PostFiat envelopes
- **Network fees**: Variable transaction costs based on network conditions
- **Confirmation time**: ~4 second ledger close time for message delivery
- **Rate limits**: Network-imposed transaction frequency restrictions

#### 7.3 Development Constraints
- **SDK compatibility**: Work within existing TypeScript SDK capabilities
- **Testing requirements**: Comprehensive test coverage for crypto operations
- **Documentation**: Extensive developer documentation and examples
- **Accessibility**: WCAG 2.1 compliance for broad user access

### 8. Success Metrics

#### 8.1 Technical Metrics
- **Message delivery**: >99% successful ledger-based message delivery
- **Performance**: <5 second average message send-to-receive time
- **Security**: Zero cryptographic vulnerabilities in security audit
- **Reliability**: <1% message loss rate during network interruptions

#### 8.2 User Experience Metrics
- **Adoption**: >100 unique users within first month of release
- **Engagement**: >80% of users complete onboarding flow
- **Satisfaction**: >4.0/5.0 average user rating
- **Documentation**: >90% of developer questions answered by docs

#### 8.3 Educational Metrics
- **Developer adoption**: >50 developers clone and study the codebase
- **Integration examples**: >10 derivative applications using PostFiat
- **Community engagement**: >25 GitHub stars and >5 community contributions
- **Compliance validation**: >3 regulatory compliance assessments

### 9. Development Phases

#### Phase 1: Core Infrastructure (Weeks 1-2)
- XRPL integration and wallet management
- Basic message envelope creation and parsing
- Local storage and state management
- Basic UI layout and navigation

#### Phase 2: Communication Features (Weeks 3-4)
- Message composition and sending
- Ledger polling and message receipt
- Basic encryption/decryption operations
- Simple chat interface

#### Phase 3: Advanced Features (Weeks 5-6)
- Context reference implementation
- Selective disclosure controls
- Audit trail visualization
- Key management dashboard

#### Phase 4: Polish and Documentation (Weeks 7-8)
- Performance optimization
- Security hardening
- Comprehensive documentation
- User experience refinement

### 10. Risk Assessment

#### 10.1 Technical Risks
- **XRPL network stability**: Dependency on external blockchain infrastructure
- **Browser crypto performance**: Potential performance bottlenecks with encryption
- **Key management complexity**: Risk of user key loss or confusion
- **Scalability concerns**: Polling efficiency with large message volumes

#### 10.2 User Experience Risks
- **Crypto complexity**: Users overwhelmed by cryptographic concepts
- **Network costs**: XRP transaction fees may deter usage
- **Onboarding friction**: Complex setup process may reduce adoption
- **Performance expectations**: Users expect instant messaging experience

#### 10.3 Mitigation Strategies
- **Fallback mechanisms**: Graceful degradation when XRPL is unavailable
- **Performance optimization**: Efficient polling and caching strategies
- **UX simplification**: Abstract cryptographic complexity behind intuitive interface
- **Cost transparency**: Clear fee estimation and batch processing options

### 11. Success Criteria

The PostFiat React Chat App will be considered successful when:

1. **Technical Excellence**: Demonstrates robust ledger-based communication with <1% message loss
2. **Developer Adoption**: Becomes the primary reference for PostFiat integration
3. **User Understanding**: Users can successfully send encrypted messages with selective disclosure
4. **Regulatory Value**: Provides clear audit trails suitable for compliance requirements
5. **Community Impact**: Spawns derivative applications and protocol extensions

### 12. Conclusion

The PostFiat React Chat App represents a critical milestone in demonstrating how cryptographic messaging can provide both privacy and auditability through blockchain-based communication. By implementing pure ledger-based architecture with selective disclosure, the application will serve as both a technical reference and a compelling demonstration of PostFiat's unique capabilities.

The success of this application will validate the PostFiat protocol's approach to solving the fundamental tension between privacy and transparency in digital communication, paving the way for broader adoption in compliance-critical environments.