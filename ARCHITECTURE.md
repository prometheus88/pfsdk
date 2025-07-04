# PostFiat SDK Architecture

This document describes the technical architecture and technology stack of the PostFiat SDK, a modern proto-first Python SDK with AI integration capabilities.

## 🎯 Architecture Overview

The PostFiat SDK is built on a **proto-first, API-driven architecture** that automatically generates type-safe Python code, REST APIs, and AI-powered integrations from Protocol Buffer definitions.

```mermaid
graph TB
    subgraph "Source of Truth"
        A[Protocol Buffers<br/>(.proto files)]
    end
    
    subgraph "Code Generation Layer"
        B[Buf CLI<br/>Protobuf → Python]
        C[Custom Generators<br/>Types & Services]
        D[OpenAPI Generator<br/>REST API Specs]
    end
    
    subgraph "Core SDK Layer"
        E[Pydantic Models<br/>Type Safety & Validation]
        F[SQLModel<br/>Database ORM]
        G[FastAPI<br/>REST API Server]
        H[gRPC Services<br/>High Performance RPC]
    end
    
    subgraph "AI Integration Layer"
        I[PydanticAI<br/>AI Agent Framework]
        J[LLM Integrations<br/>OpenAI, Anthropic, etc.]
    end
    
    subgraph "Client Layer"
        K[Python SDK<br/>Type-safe Client]
        L[REST API<br/>HTTP/JSON Interface]
        M[gRPC Client<br/>Binary Protocol]
    end
    
    A --> B
    A --> C
    A --> D
    B --> E
    C --> E
    C --> F
    E --> G
    E --> H
    E --> I
    F --> G
    I --> J
    E --> K
    G --> L
    H --> M
```

## 🛠️ Technology Stack

### 1. Protocol Buffers (Proto3)
**Role:** Single source of truth for all data structures and service definitions

**Why Protocol Buffers:**
- **Language agnostic:** Generate code for multiple languages
- **Schema evolution:** Backward/forward compatibility
- **Performance:** Efficient binary serialization
- **Type safety:** Strong typing across all generated code
- **Documentation:** Self-documenting schemas

**Usage:**
```protobuf
syntax = "proto3";
package postfiat.v3;

message ContextualMessage {
  string content = 1;
  MessageType type = 2;
  EncryptionMode encryption = 3;
}

enum MessageType {
  CONTEXTUAL_MESSAGE = 0;
  MULTIPART_MESSAGE_PART = 1;
}

service WalletService {
  rpc CreateWallet(CreateWalletRequest) returns (CreateWalletResponse);
  rpc GetBalance(GetBalanceRequest) returns (GetBalanceResponse);
}
```

### 2. OpenAPI 3.0
**Role:** REST API specification and documentation generation

**Why OpenAPI:**
- **API-first design:** Design APIs before implementation
- **Auto-documentation:** Interactive API docs with Swagger UI
- **Client generation:** Generate clients for multiple languages
- **Validation:** Request/response validation
- **Tooling ecosystem:** Rich ecosystem of tools and integrations

**Generated from Proto:**
- REST endpoints for each gRPC service method
- JSON schemas for all message types
- Interactive documentation
- Client SDKs for web/mobile

### 3. FastAPI
**Role:** High-performance REST API server framework

**Why FastAPI:**
- **Performance:** One of the fastest Python frameworks
- **Type hints:** Native Python type hint support
- **Auto-validation:** Automatic request/response validation
- **OpenAPI integration:** Built-in OpenAPI/Swagger support
- **Async support:** Native async/await support
- **Developer experience:** Excellent error messages and debugging

**Features:**
```python
from fastapi import FastAPI
from postfiat.models import CreateWalletRequest, CreateWalletResponse

app = FastAPI(title="PostFiat API", version="3.0.0")

@app.post("/wallets", response_model=CreateWalletResponse)
async def create_wallet(request: CreateWalletRequest):
    # Auto-validated input, type-safe output
    return await wallet_service.create_wallet(request)
```

### 4. Pydantic v2
**Role:** Data validation, serialization, and type safety

**Why Pydantic:**
- **Type safety:** Runtime type checking and validation
- **Performance:** Fast validation with Rust core
- **JSON Schema:** Automatic JSON schema generation
- **Serialization:** Flexible serialization/deserialization
- **Integration:** Works seamlessly with FastAPI and SQLModel

**Features:**
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class WalletModel(BaseModel):
    id: str = Field(..., description="Unique wallet identifier")
    balance: float = Field(ge=0, description="Wallet balance")
    created_at: datetime
    metadata: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "wallet_123",
                "balance": 100.50,
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
```

### 5. PydanticAI
**Role:** AI agent framework for intelligent automation

**Why PydanticAI:**
- **Type safety:** Type-safe AI interactions with Pydantic models
- **Multi-LLM:** Support for OpenAI, Anthropic, Google, etc.
- **Structured output:** Guaranteed structured responses
- **Tool integration:** Easy function calling and tool use
- **Validation:** Automatic validation of AI responses

**Features:**
```python
from pydantic_ai import Agent
from postfiat.models import WalletAnalysis, TransactionData

wallet_agent = Agent(
    'openai:gpt-4',
    result_type=WalletAnalysis,
    system_prompt="Analyze wallet transactions and provide insights."
)

async def analyze_wallet(transactions: list[TransactionData]) -> WalletAnalysis:
    result = await wallet_agent.run(
        f"Analyze these {len(transactions)} transactions",
        deps={"transactions": transactions}
    )
    return result.data  # Type-safe WalletAnalysis object
```

### 6. SQLModel
**Role:** Database ORM with type safety and async support

**Why SQLModel:**
- **Type safety:** SQLAlchemy with Pydantic validation
- **Async support:** Native async database operations
- **FastAPI integration:** Seamless integration with FastAPI
- **Migration support:** Alembic integration for schema migrations
- **Performance:** Efficient queries with SQLAlchemy Core

**Features:**
```python
from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional

class Wallet(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    balance: float = Field(default=0.0, ge=0)
    currency: str = Field(default="USD")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Automatic Pydantic validation + SQLAlchemy ORM
```

## 🏗️ Architectural Patterns

### 1. Proto-First Development
**Pattern:** All data structures and services defined in Protocol Buffers first

**Benefits:**
- Single source of truth
- Automatic code generation
- Cross-language compatibility
- Schema evolution support

### 2. Layered Architecture
**Layers:**
1. **Data Layer:** SQLModel + Database
2. **Service Layer:** Business logic and gRPC services
3. **API Layer:** FastAPI REST endpoints
4. **Client Layer:** Generated SDK clients

### 3. Code Generation Pipeline
**Process:**
1. Define schemas in `.proto` files
2. Generate Python classes with Buf
3. Generate Pydantic models and FastAPI routes
4. Generate SQLModel database models
5. Generate client SDKs and documentation

### 4. AI-First Integration
**Pattern:** AI capabilities built into core SDK functionality

**Implementation:**
- PydanticAI agents for intelligent automation
- Type-safe AI interactions
- Structured AI responses with validation
- Multi-LLM support for flexibility

## 🔄 Data Flow Architecture

### Request Flow (REST API)
```
Client Request → FastAPI → Pydantic Validation → Service Layer → SQLModel → Database
                    ↓
Client Response ← JSON Serialization ← Pydantic Model ← Service Response ← Query Result
```

### Request Flow (gRPC)
```
gRPC Client → Protobuf Deserialization → Service Implementation → SQLModel → Database
                    ↓
gRPC Response ← Protobuf Serialization ← Service Response ← Query Result
```

### AI Integration Flow
```
User Input → PydanticAI Agent → LLM API → Structured Response → Pydantic Validation → Action
```

## 🚀 Performance Characteristics

### Serialization Performance
- **Protobuf:** ~10x faster than JSON for binary protocols
- **Pydantic v2:** ~5-50x faster validation than v1
- **FastAPI:** Comparable to Node.js and Go frameworks

### Database Performance
- **SQLModel:** Async operations with connection pooling
- **Query optimization:** SQLAlchemy Core for complex queries
- **Caching:** Redis integration for frequently accessed data

### AI Performance
- **Parallel processing:** Concurrent AI agent execution
- **Caching:** Response caching for repeated queries
- **Streaming:** Real-time AI response streaming

## 🔒 Security Architecture

### API Security
- **Authentication:** JWT tokens with FastAPI security
- **Authorization:** Role-based access control (RBAC)
- **Rate limiting:** Request throttling and abuse prevention
- **Input validation:** Comprehensive Pydantic validation

### Data Security
- **Encryption:** At-rest and in-transit encryption
- **SQL injection prevention:** SQLModel parameterized queries
- **Data validation:** Multi-layer validation (Pydantic + Database)

### AI Security
- **Prompt injection protection:** Input sanitization
- **Output validation:** Structured response validation
- **API key management:** Secure credential handling

## 📊 Monitoring and Observability

### Metrics
- **API metrics:** Request/response times, error rates
- **Database metrics:** Query performance, connection pools
- **AI metrics:** Token usage, response times, success rates

### Logging
- **Structured logging:** JSON logs with correlation IDs
- **Error tracking:** Comprehensive error reporting
- **Audit trails:** User action logging

### Health Checks
- **Service health:** Database, AI services, external APIs
- **Dependency monitoring:** Real-time dependency status
- **Performance monitoring:** Response time tracking

## 🔮 Future Architecture Considerations

### Scalability
- **Microservices:** Service decomposition as needed
- **Event streaming:** Apache Kafka for event-driven architecture
- **Caching layers:** Redis for performance optimization

### AI Evolution
- **Multi-modal AI:** Support for vision, audio, and text
- **Custom models:** Fine-tuned models for domain-specific tasks
- **Edge AI:** Local AI processing capabilities

### Integration Expansion
- **Blockchain integration:** Web3 and cryptocurrency support
- **Real-time features:** WebSocket support for live updates
- **Mobile SDKs:** Native mobile SDK generation

This architecture provides a solid foundation for building scalable, type-safe, and AI-powered financial applications while maintaining developer productivity and code quality. 🎯
