# PostFiat SDK Documentation

Welcome to the PostFiat SDK documentation. This is a proto-first, multi-language SDK with Python, TypeScript, and Solidity support.

## Latest Release: release-0.1.0-rc1

## Quick Start

### Python
```bash
# Install from PyPI (when published)
pip install postfiat-sdk==0.1.0-rc1

# Or download from GitHub releases
# wget https://github.com/allenday/pfsdk/releases/download/release-0.1.0-rc1/postfiat-sdk-0.1.0-rc1.whl
# pip install postfiat-sdk-0.1.0-rc1.whl
```

### TypeScript
```bash
# Install from npm (when published)
npm install @postfiat/sdk@0.1.0-rc1

# Or download from GitHub releases
# wget https://github.com/allenday/pfsdk/releases/download/release-0.1.0-rc1/postfiat-sdk-0.1.0-rc1.tgz
# npm install postfiat-sdk-0.1.0-rc1.tgz
```

### Solidity
```bash
# Clone the repository for Solidity development
git clone https://github.com/postfiat/pfsdk.git
cd pfsdk

# Install dependencies and generate contracts
make sol-deps
make proto
make sol-build
```

## Features

- **Proto-first architecture**: Single source of truth for all APIs
- **Multi-language support**: Python, TypeScript, and Solidity SDKs
- **Type-safe**: Generated types and validation across all languages
- **Modern tooling**: FastAPI, Pydantic, React hooks, Foundry
- **AI integration**: PydanticAI support for agents
- **Blockchain integration**: Smart contract generation and deployment

## API Documentation

- **[Python SDK API](generated/python/index.html)** - Complete Python API reference with mkdocstrings
- **[TypeScript SDK API](generated/typescript/index.html)** - Complete TypeScript API reference with TypeDoc
- **[Solidity Integration](solidity/README.md)** - Smart contract development guide
- **[OpenAPI Specification](api/openapi.md)** - Interactive REST API documentation
- **[Protocol Buffers](generated/proto/index.md)** - Proto message definitions

## Architecture

The SDK follows a [proto-first architecture](ARCHITECTURE.md) where Protocol Buffer definitions drive code generation for multiple languages and platforms, including smart contracts.

## Development

See the [Development Guide](DEVELOPMENT.md) for information on contributing to the SDK.