# PostFiat SDK Development Guide

This document describes the code generation architecture and development processes for the PostFiat SDK.

## 🎯 Architecture Overview

The PostFiat SDK follows a **proto-first architecture** where Protocol Buffer definitions are the single source of truth for all generated code across multiple languages and platforms.

### Multi-Language Support

The SDK now supports multiple programming languages with a shared proto definition:

```
pfsdk/
├── proto/                    # Shared protocol buffer definitions
│   ├── buf.gen.yaml         # Multi-language generation config
│   └── postfiat/v3/         # Proto schema definitions
├── python/                   # Python SDK
│   ├── postfiat/            # Python package
│   ├── scripts/             # Python-specific generators
│   └── tests/               # Python test suites
├── typescript/              # TypeScript SDK
│   ├── src/                 # TypeScript source code
│   ├── scripts/             # TypeScript generation scripts
│   └── tests/               # TypeScript test suites
├── solidity/                # Solidity SDK
│   ├── src/                 # Solidity source code
│   ├── src/generated/       # Generated Solidity contracts
│   ├── test/                # Solidity test suites
│   └── foundry.toml         # Foundry configuration
└── docs/                    # Shared documentation
```

```mermaid
graph TD
    A[Proto Files] --> B[Buf Generate]
    B --> C[Python Protobuf Classes]
    B --> D[TypeScript Protobuf Classes]
    A --> E[Protobuf3-Solidity Generator]
    E --> F[Solidity Libraries & Structs]
    A --> G[Python Type Generator]
    G --> H[Pydantic Enums]
    G --> I[Exception Classes]
    A --> J[Comprehensive Generator]
    J --> K[SDK Managers]
    J --> L[Client Stubs]
    J --> M[OpenAPI Specs]
    A --> N[Test Generator]
    N --> O[Contract Tests]
    N --> P[Serialization Tests]
    N --> Q[Integration Tests]
    A --> R[TypeScript Type Generator]
    R --> S[TypeScript Enums]
    R --> T[Exception Classes]
    R --> U[Client SDK]
    D --> V[TypeScript SDK]
    V --> W[React Hooks]
    V --> X[Web Client]
    F --> Y[Solidity Contracts]
    Y --> Z[EVM Integration]
```

## 🔧 Code Generation Pipeline

### 1. Protocol Buffer Generation

**Tool:** [Buf CLI](https://buf.build/)
**Config:** `proto/buf.gen.yaml`
**Command:** `buf generate --template buf.gen.yaml`

**Generates:**
- `python/postfiat/v3/*_pb2.py` - Python message classes
- `python/postfiat/v3/*_pb2_grpc.py` - Python gRPC service stubs
- `typescript/src/generated/*_pb.ts` - TypeScript message classes
- `typescript/src/generated/*_connect.ts` - TypeScript gRPC-Web service stubs

**Example:**
```bash
cd proto
buf generate --template buf.gen.yaml
```

### 2. Python Type Generation

**Script:** `python/scripts/generate_python_types.py`
**Purpose:** Generate Pydantic-compatible types from protobuf enums

**Generates:**
- `python/postfiat/types/enums.py` - Pydantic enum classes
- `python/postfiat/exceptions.py` - SDK exception hierarchy

**Features:**
- Automatic enum extraction from protobuf
- Pydantic compatibility with conversion methods
- Standard exception hierarchy for SDK errors

**Example:**
```python
# Generated enum usage
from postfiat.types.enums import MessageType, EncryptionMode

msg_type = MessageType.CONTEXTUAL_MESSAGE
encryption = EncryptionMode.NACL_SECRETBOX

# Convert to/from protobuf
pb_value = msg_type.to_protobuf()
pydantic_value = MessageType.from_protobuf(pb_value)
```

### 3. Solidity Contract Generation

**Tool:** [Protobuf3-Solidity](https://github.com/allenday/protobuf3-solidity)
**Purpose:** Generate Solidity contracts and libraries from protobuf definitions

**Generates:**
- `solidity/src/generated/postfiat/v3/` - PostFiat protobuf contracts
- `solidity/src/generated/a2a/v1/` - A2A protobuf contracts  
- `solidity/src/generated/google/protobuf/` - Google protobuf types

**Features:**
- Automatic struct and enum generation from protobuf
- Type-safe contract interfaces
- Library-based organization for reusability
- Foundry integration for modern Solidity development
- Seamless integration with Python and TypeScript SDKs

**Example:**
```solidity
// Auto-generated from protobuf definitions
library Postfiat_V3 {
    struct ContextualMessage {
        string content;
        MessageType message_type;
        EncryptionMode encryption;
    }
    
    enum MessageType {
        CONTEXTUAL_MESSAGE,
        MULTIPART_MESSAGE_PART
    }
    
    enum EncryptionMode {
        NONE,
        NACL_SECRETBOX,
        AES_256_GCM
    }
}
```

**Build System:**
```bash
# Generate Solidity contracts
make proto

# Build contracts with Foundry
make sol-build

# Run Solidity tests
make sol-test
```

### 4. TypeScript Type Generation

**Script:** `typescript/scripts/generate-typescript-types.ts`
**Purpose:** Generate TypeScript types and SDK components from protobuf definitions

**Generates:**
- `typescript/src/types/enums.ts` - TypeScript enum classes with conversion utilities
- `typescript/src/types/exceptions.ts` - SDK exception hierarchy
- `typescript/src/client/base.ts` - Base client infrastructure
- `typescript/src/hooks/index.ts` - React hooks for web integration
- `typescript/src/index.ts` - Main SDK export file

**Features:**
- Automatic enum extraction from protobuf
- gRPC-Web client support via Connect-ES
- React hooks for modern web development
- Type-safe error handling
- Conversion utilities between proto and TypeScript types

**Example:**
```typescript
// Generated enum usage
import { MessageType, EncryptionMode } from '@postfiat/sdk';

const msgType = MessageType.CONTEXTUAL_MESSAGE;
const encryption = EncryptionMode.NACL_SECRETBOX;

// Convert to/from protobuf
const pbValue = MessageType.toProtobuf(msgType);
const tsValue = MessageType.fromProtobuf(pbValue);
```

### 5. Comprehensive SDK Generation

**Script:** `python/scripts/generate_protobuf.py`
**Purpose:** Generate complete SDK components from protobuf definitions

**Generates:**
- `python/postfiat/models/envelope_enums.py` - Message envelope enums
- `python/postfiat/managers/` - Service manager classes
- `python/postfiat/services/` - Service implementation stubs
- `python/postfiat/clients/` - Client wrapper classes
- `python/postfiat/integrations/discord/` - Discord command mappers
- `api/` - OpenAPI/Swagger specifications

**Features:**
- Automatic service discovery from protobuf
- Manager pattern for service orchestration
- Client stubs for easy API consumption
- OpenAPI generation for REST endpoints
- Discord integration for command handling

### 6. TypeScript Test Generation

**Script:** `typescript/scripts/generate-typescript-tests.ts`
**Purpose:** Generate comprehensive TypeScript test suites from protobuf definitions

**Generates:**
- `typescript/tests/generated/enums.test.ts` - Enum conversion and validation tests
- `typescript/tests/generated/exceptions.test.ts` - Exception handling tests
- `typescript/tests/generated/client.test.ts` - Client SDK tests
- `typescript/tests/generated/hooks.test.ts` - React hooks tests
- `typescript/tests/generated/integration.test.ts` - Integration test suite

**Features:**
- Jest-based testing framework
- Comprehensive enum testing (conversion, validation, edge cases)
- Exception hierarchy testing
- Client SDK integration testing
- React hooks testing with modern patterns

### 7. Solidity Test Generation

**Tool:** Foundry (forge)
**Purpose:** Test generated Solidity contracts and custom contract implementations

**Test Structure:**
- `solidity/test/` - Manual test files
- `solidity/src/generated/` - Generated contract files (tested via integration)

**Features:**
- Foundry-based testing framework
- Gas optimization testing
- Contract integration testing
- Protobuf serialization/deserialization testing
- Cross-language compatibility testing

**Example:**
```solidity
// Test generated protobuf contracts
contract PostfiatV3Test is Test {
    function testContextualMessage() public {
        Postfiat_V3.ContextualMessage memory msg = Postfiat_V3.ContextualMessage({
            content: "Hello, World!",
            message_type: Postfiat_V3.MessageType.CONTEXTUAL_MESSAGE,
            encryption: Postfiat_V3.EncryptionMode.NACL_SECRETBOX
        });
        
        assertEq(msg.content, "Hello, World!");
        assertEq(uint8(msg.message_type), uint8(Postfiat_V3.MessageType.CONTEXTUAL_MESSAGE));
    }
}
```

**Testing Commands:**
```bash
# Run all Solidity tests
make sol-test

# Run specific test file
cd solidity && forge test --match-contract PostfiatV3Test

# Run with gas reporting
cd solidity && forge test --gas-report
```
- Auto-generated test data and scenarios

### 6. Test Generation

**🆕 Dynamic Test Generator (Recommended):**
**Script:** `python/scripts/generate_dynamic_protobuf_tests.py`
**Purpose:** Generate comprehensive test suites using runtime proto introspection

**Generates:**
- `python/tests/generated/test_dynamic_serialization.py` - Round-trip serialization tests
- `python/tests/generated/test_dynamic_validation.py` - Field and enum validation tests
- `python/tests/generated/test_dynamic_services.py` - gRPC service method tests
- `python/tests/generated/test_dynamic_evolution.py` - Schema evolution and compatibility tests

**Key Features:**
- **Runtime Introspection:** Uses actual proto message descriptors (no hardcoded field names)
- **Auto-Adaptation:** Tests automatically adapt when proto schemas change
- **Schema Evolution:** Tests backward compatibility and wire format stability
- **Comprehensive Coverage:** Generates tests for all discovered proto messages

**Test Types:**
- **Serialization Integrity:** Validates round-trip serialization
- **Field Type Validation:** Tests field constraints and types
- **Enum Validation:** Verifies enum values and conversions
- **Service Integration:** Tests service method signatures
- **Schema Evolution:** Tests backward compatibility and field number stability

## 📦 Version Management

### Centralized Version System

The PostFiat SDK uses a **centralized version management** system to ensure consistency across all packages and artifacts.

**Central Source of Truth:**
```
VERSION                           # Single source of truth for all version numbers
```

**Version Flow:**
```mermaid
graph TD
    A[VERSION file] --> B[Python Generator]
    A --> C[TypeScript Update Script]
    B --> D[python/pyproject.toml - dynamic]
    B --> E[python/postfiat/__init__.py]
    C --> F[typescript/package.json]
    C --> G[typescript/src/index.ts]
    C --> H[typescript/src/client/base.ts User-Agent]
```

### Updating Versions

**Automated Update (Recommended):**
```bash
# Update VERSION file
echo "0.2.0-rc2" > VERSION

# Update all packages automatically
./scripts/update-all-versions.sh
```

**Manual Component Updates:**
```bash
# Python packages only
cd python && python scripts/generate_python_types.py

# TypeScript packages only  
cd typescript && npm run update-version
```

**Generated Files:**
- `python/pyproject.toml`: Uses dynamic versioning via `setup.py`
- `python/postfiat/__init__.py`: `__version__ = "0.2.0-rc2"`
- `typescript/package.json`: `"version": "0.2.0-rc2"`
- `typescript/src/index.ts`: `export const VERSION = '0.2.0-rc2'`
- `typescript/src/client/base.ts`: User-Agent header with version

**Version Validation:**
```bash
# Check Python version
cd python && python -c "import postfiat; print(postfiat.__version__)"

# Check TypeScript version  
cd typescript && node -e "console.log(require('./package.json').version)"

# Verify all versions match
./scripts/update-all-versions.sh | grep "Version:"
```

### Release Process

1. **Update VERSION file:** `echo "0.2.0-rc2" > VERSION`
2. **Update all packages:** `./scripts/update-all-versions.sh`
3. **Test changes:** Run test suites across all packages
4. **Commit changes:** `git add . && git commit -m "feat: bump to 0.2.0-rc2"`
5. **Create release tag:** `git tag release-0.2.0-rc2 && git push --tags`
6. **CI builds artifacts:** GitHub Actions automatically creates release artifacts

## 🔄 Development Workflow

### Local Development

1. **Edit Proto Files:**
   ```bash
   # Edit proto/postfiat/v3/*.proto
   vim proto/postfiat/v3/messages.proto
   ```

2. **Generate Code:**
   ```bash
   # Generate protobuf classes
   cd proto && buf generate --template buf.gen.yaml && cd ..
   
   # Generate Python types and tests
   cd python && python scripts/generate_python_types.py
   python scripts/generate_protobuf.py
   python scripts/generate_dynamic_protobuf_tests.py && cd ..
   
   # Generate TypeScript SDK
   cd typescript && npm run generate:all && cd ..
   ```

3. **Test Changes:**
   ```bash
   # Run Python tests
   cd python && pytest tests/ -v && cd ..
   
   # Run TypeScript tests
   cd typescript && npm test && cd ..
   
   # Test specific components
   python -c "from postfiat.v3 import messages_pb2; print('✅ Protobuf import works')"
   python -c "from postfiat.types.enums import MessageType; print('✅ Enums work')"
   ```

### CI/CD Pipeline

The CI automatically handles code generation and releases:

**Code Generation Job:**
1. Install dependencies (buf, python packages, node.js)
2. Generate protobuf classes for Python and TypeScript
3. Generate Python types and tests
4. Generate TypeScript types and React hooks
5. Run complete test suite

**Release Job (release-* tags):**
1. Generate all code from protobuf definitions
2. Build Python packages (.whl and .tar.gz)
3. Build TypeScript packages (.tgz)
4. Create GitHub release with attached artifacts
5. No automatic publishing to npm/PyPI (manual control)

## 📁 Generated File Management

### .gitignore Strategy

**Ignored (Generated) Files:**
```gitignore
# Generated protobuf Python files
python/postfiat/v3/*_pb2.py
python/postfiat/v3/*_pb2_grpc.py

# Generated Python types
python/postfiat/types/enums.py
python/postfiat/exceptions.py
python/postfiat/models/envelope_enums.py

# Generated SDK components
python/postfiat/managers/
python/postfiat/services/
python/postfiat/clients/
python/postfiat/integrations/

# Generated TypeScript files
typescript/src/generated/
typescript/src/client/
typescript/src/types/
typescript/src/index.ts
typescript/tests/generated/
typescript/dist/

# Generated tests
python/tests/generated/

# Generated API documentation
api/
```

**Committed (Source) Files:**
- `proto/` - Protocol buffer definitions
- `scripts/` - Generation scripts
- `python/postfiat/__init__.py` - Python package root
- `python/postfiat/client/base.py` - Python base client infrastructure
- `typescript/src/hooks/` - TypeScript React hooks (non-generated)
- `typescript/package.json` - TypeScript package configuration
- `tests/manual/` - Manual tests

### Branch-Specific Behavior

**Dev Branch:**
- Generated files ignored via .gitignore
- Clean source-only development
- Developers run generation locally

**Release Strategy:**
- Use git tags with "release-" prefix (e.g., release-0.1.0-rc1)
- CI automatically builds and attaches Python/TypeScript packages
- No automatic publishing to npm/PyPI registries
- GitHub releases contain downloadable artifacts

## 🧪 Testing Architecture

### Test Organization

```
python/tests/
├── manual/                    # Manual tests (committed)
│   ├── test_client_integration.py
│   ├── test_business_logic.py
│   └── test_edge_cases.py
└── generated/                 # Auto-generated tests (ignored)
    ├── test_dynamic_serialization.py    # 🆕 Dynamic serialization tests
    ├── test_dynamic_validation.py       # 🆕 Dynamic field/enum validation
    ├── test_dynamic_services.py         # 🆕 Dynamic service tests
    ├── test_dynamic_evolution.py        # 🆕 Schema evolution tests
    ├── test_contract_validation.py      # Legacy hardcoded tests
    ├── test_serialization_integrity.py  # Legacy hardcoded tests
    └── test_persistence_scaffolding.py  # Legacy hardcoded tests

typescript/tests/
├── manual/                    # Manual tests (committed)
│   ├── integration/          # Integration tests
│   │   └── selective-disclosure.test.ts  # 🎯 Enhanced 3,048 scenario test
│   └── unit/                 # Unit tests
│       └── PostFiatCrypto.test.ts
└── generated/                # Auto-generated tests (ignored)
    ├── enums.test.ts
    ├── exceptions.test.ts
    ├── client.test.ts
    └── hooks.test.ts
```

### Test Types

**Manual Tests:**
- Business logic validation
- Integration testing
- Edge case handling
- User workflow testing
- **Selective disclosure testing** (TypeScript: 3,048 scenarios)

**Generated Tests (Dynamic):**
- Runtime proto introspection-based testing
- Serialization round-trip testing with actual field discovery
- Field constraint validation using proto descriptors
- Enum value verification from runtime schema
- Service method signature testing
- Schema evolution and backward compatibility testing

### 🎯 Selective Disclosure Test Enhancement

The TypeScript SDK includes a comprehensive selective disclosure integration test that validates 3,048 unique scenarios across multiple dimensions:

**Test Location:** `typescript/tests/manual/integration/selective-disclosure.test.ts`

**Test Dimensions:**
1. **Base Scenarios (432):** Original permutation test from SDK v0.1.0-rc15
   - Sender sequences: AAA, AAB, ABA, ABB, BAA, BAB, BBA, BBB
   - Encryption modes: NONE, PROTECTED, PUBLIC_KEY
   - Initial recipients: broadcast, direct
   - Public/private reference counts: 0, 1, 2

2. **AccessGrant Complexity (+864 scenarios):**
   - Single content key grant
   - Single group key grant
   - Multiple content key grants
   - Multiple group key grants
   - Mixed content + group key grants

3. **Context DAG Depth (+432 scenarios):**
   - Deep context chains (0-5 levels)
   - Circular reference detection
   - Branching DAG structures
   - Partial access scenarios

4. **Multi-Group Access Patterns (+672 scenarios):**
   - Single group membership
   - Multiple same-level groups
   - Multiple different access levels
   - Hierarchical group relationships
   - Overlapping group memberships
   - Exclusive group access patterns

**Key Features:**
- **PostFiat Opinionated Crypto:** Uses one-line encryption/decryption APIs
- **100% Pass Rate:** All 6,096 test executions pass (3,048 scenarios × 2 observers)
- **Fast Execution:** ~2 seconds for full test suite
- **v3 Protocol Compliance:** Uses AccessGrant system and proper ContextReference handling

**Running the Test:**
```bash
cd typescript
npm run test:selective-disclosure
```

## 🔧 Extending the SDK

### Adding New Proto Files

1. **Create proto file:**
   ```protobuf
   // proto/postfiat/v3/new_service.proto
   syntax = "proto3";
   package postfiat.v3;
   
   service NewService {
     rpc DoSomething(DoSomethingRequest) returns (DoSomethingResponse);
   }
   ```

2. **Regenerate code:**
   ```bash
   python scripts/generate_protobuf.py
   ```

3. **Generated automatically:**
   - Service manager class
   - Client stub
   - gRPC service implementation
   - OpenAPI specification
   - Integration tests

### Adding Custom Generators

1. **Create generator script:**
   ```python
   # scripts/generate_custom_component.py
   def generate_custom_component():
       # Your generation logic
       pass
   ```

2. **Add to CI pipeline:**
   ```yaml
   - name: Generate custom component
     run: python scripts/generate_custom_component.py
   ```

## 📊 Monitoring and Debugging

### Structured Logging

**Dependencies:**
- **structlog:** Structured logging with rich context
- **loguru:** Beautiful console output and formatting

**Usage in Development:**
```python
from postfiat.logging import get_logger

logger = get_logger("my_component")
logger.info("Processing request", user_id="123", action="create_wallet")
```

**Environment-Aware Output:**
- **Development/Testing:** Human-readable console output
- **Production:** JSON structured logs
- **pytest:** Plain text for test readability

### Generation Logs

All generation scripts provide detailed structured logging:
```bash
python scripts/generate_python_types.py
# {"event": "Starting protobuf-based type generation", "level": "info", "timestamp": "2025-07-04T16:20:00.123Z"}
# {"enum_types_count": 5, "modules": ["messages", "errors"], "event": "Discovered protobuf definitions", "level": "info"}
# ✅ Generated /path/to/postfiat/types/enums.py
# ✅ Generated /path/to/postfiat/exceptions.py

python scripts/generate_dynamic_protobuf_tests.py
# 🎯 NEW: Dynamic Proto Test Generation with Runtime Introspection
# {"event": "Discovered 10 proto message classes", "level": "info", "timestamp": "2025-07-07T10:35:16.856532Z"}
# {"event": "✅ Generated serialization tests: tests/generated/test_dynamic_serialization.py", "level": "info"}
# {"event": "✅ Generated evolution tests: tests/generated/test_dynamic_evolution.py", "level": "info"}
# ✅ SUCCESS: Dynamic proto test generation complete!

python scripts/generate_protobuf.py
# 🚀 Generating comprehensive SDK from protobuf definitions...
# 📊 Found 3 message types and 0 services
# 📝 Generated envelope enums for 3 message types
# ✅ Generation complete!
```

### CI Debugging

Check GitHub Actions for detailed logs:
1. Go to Actions tab
2. Click on failed workflow
3. Expand job steps to see generation output
4. Look for specific error messages

### Common Issues

**Import Errors:**
- Ensure all dependencies installed: `pip install -e .`
- Check namespace consistency: `postfiat.v3` vs `postfiat.wallet.v3`

**Generation Failures:**
- Verify proto syntax: `buf lint`
- Check buf configuration: `buf.yaml` and `buf.gen.yaml`
- Ensure all imports available

**Test Failures:**
- Regenerate dynamic tests: `cd python && python scripts/generate_dynamic_protobuf_tests.py`
- Use CI integration: `cd python && python scripts/ci_test_generation.py --force`
- Check protobuf message compatibility
- Verify enum values match proto definitions
- For legacy tests: `cd python && python scripts/generate_protobuf_tests.py` *(deprecated)*

## � Logging Best Practices

### When to Add Logging

**✅ DO Log:**
- **Factory functions:** Exception creation, object construction
- **Utility methods:** Data processing, transformations
- **API middleware:** Request/response processing
- **Service boundaries:** External API calls, database operations
- **Error handling:** Exception processing and recovery

**❌ DON'T Log:**
- **Pure data classes:** Pydantic models, simple exception classes
- **Getters/setters:** Simple property access
- **Constructors:** Basic object initialization without side effects
- **Pure functions:** Mathematical operations, simple transformations

### Logging Patterns

**Structured Context:**
```python
logger.info(
    "Processing user request",
    user_id=user.id,
    action="create_wallet",
    request_id=request_id,
    duration_ms=elapsed_time
)
```

**Error Logging:**
```python
logger.error(
    "Database operation failed",
    operation="insert_wallet",
    table="wallets",
    error_code=exc.error_code,
    retry_count=retry_count,
    exc_info=True  # Include stack trace
)
```

**Debug Information:**
```python
logger.debug(
    "Cache operation",
    cache_key=key,
    cache_hit=hit,
    ttl_seconds=ttl
)
```

### Generated Code Logging

The code generators automatically add logging to:
- **Exception factory functions:** `create_exception_from_error_code()`
- **Error processing utilities:** `create_exception_from_error_info()`
- **Serialization methods:** `PostFiatError.to_dict()`
- **Test generation:** Discovery and generation progress

Pure data classes (enums, simple exceptions) remain clean without logging.

## 🚀 Performance Considerations

### Generation Speed

- **Incremental generation:** Only regenerate changed components
- **Parallel processing:** Use multiple cores where possible
- **Caching:** Cache generated artifacts between runs

### Runtime Performance

- **Lazy imports:** Import generated modules only when needed
- **Connection pooling:** Reuse gRPC connections
- **Serialization optimization:** Use efficient protobuf serialization

## 📋 Best Practices

1. **Proto-first development:** Always start with proto definitions
2. **Consistent naming:** Follow protobuf naming conventions
3. **Backward compatibility:** Use field numbers carefully
4. **Documentation:** Document proto files thoroughly
5. **Testing:** Test both manual and generated components
6. **Version management:** Use semantic versioning for releases

This architecture ensures maintainable, scalable, and robust SDK development with minimal manual overhead. 🎯

## 🛠️ Build & Test Workflow (Unified)

The Makefile at the project root now orchestrates all major development tasks for both Python and TypeScript SDKs. Use these targets for a consistent workflow:

### Setup
```bash
make dev-setup  # Installs all dependencies and generates code
```

### Code Generation
```bash
make proto      # Generate protobuf classes
make types      # Generate Python types
make tests      # Generate dynamic proto tests (Python)
make regen-all  # Regenerate everything (proto + types + tests)
```

### Testing
```bash
make tests-manual   # Run manual Python tests
make tests-core     # Run core dynamic Python tests
make tests-all      # Run all generated Python tests
make ts-build       # Build TypeScript SDK
make ts-test        # Run TypeScript tests
make ts-test-all    # Run all TypeScript unit and integration tests
make test           # Run all Python and TypeScript tests (recommended)
```

- The `test` target runs both Python and TypeScript tests for full coverage.
- All TypeScript build/test commands are now available via Makefile.

## 🧪 TypeScript Test Generation

- To generate and run TypeScript tests:
```bash
make ts-test-all
```

## 🧪 Running All Tests

- To run all tests (Python + TypeScript):
```bash
make test
```

## 🚦 CI/CD Flows & Makefile-Driven Development

The PostFiat SDK uses a **Makefile-driven workflow** for all build, test, code generation, versioning, and documentation tasks. This ensures that what you run locally is exactly what CI runs, making it easy to anticipate and debug CI failures.

### CI/CD Flows

1. **Verification (PRs, pushes to dev/main):**
   - Lint, verify, and generate code from protobufs
   - Run all code generation
   - Run all tests (Python & TypeScript, all supported versions)
   - Ensure build artifacts (.whl, .tar.gz, .tgz) can be created
   - **CI:** Calls `make bump-version`, `make regen-all`, `make tests`, `make build-py`, `make build-ts`

2. **Release (on tag push):**
   - Build and upload release artifacts to GitHub Releases (Python wheels, tarballs, TypeScript tgz, etc.)
   - **CI:** Calls `make bump-version`, `make regen-all`, `make release`

3. **Docs (on merge to main):**
   - Build and publish documentation site (mkdocs, Sphinx, Swagger/OpenAPI, TypeDoc, etc.)
   - **CI:** Calls `make docs` and deploys the result

### Local Development

- **All major workflows are Makefile-driven:**
  - `make dev-setup` — Install all dependencies and generate code
  - `make regen-all` — Regenerate everything (proto + types + tests)
  - `make tests` — Run all Python and TypeScript tests (recommended)
  - `make build-py` — Build Python package(s)
  - `make build-ts` — Build TypeScript package(s)
  - `make release` — Build all release artifacts
  - `make docs` — Build all documentation

- **CI mirrors local development:**
  - All CI jobs call Makefile targets for build, test, codegen, versioning, and docs
  - No duplicated shell logic between local and CI
  - If it works locally, it will work in CI

- **Branch protection:**
  - Managed via a manual GitHub workflow (`setup-repo.yml`) for repo admins
  - Not part of the Makefile, as it is a rare, admin-only task

### Example: Running Everything Locally

```bash
make dev-setup      # One-time setup
make bump-version   # Update all version strings
make regen-all      # Regenerate all code and tests
make tests          # Run all tests (Python + TypeScript)
make build-py       # Build Python package(s)
make build-ts       # Build TypeScript package(s)
make release        # Build all release artifacts
make docs           # Build all documentation
```

- See `make help` for a full list of available targets.
- All contributors should use the Makefile for all build, test, and codegen tasks.
