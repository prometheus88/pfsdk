# PostFiat SDK Documentation

Welcome to the PostFiat SDK documentation. This is a proto-first, multi-language SDK with Python and TypeScript support.

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

## Features

- **Proto-first architecture**: Single source of truth for all APIs
- **Multi-language support**: Python and TypeScript SDKs
- **Type-safe**: Generated types and validation
- **Modern tooling**: FastAPI, Pydantic, React hooks
- **AI integration**: PydanticAI support for agents

## API Documentation

- **[Python SDK API](generated/python/index.html)** - Complete Python API reference with Sphinx
- **[OpenAPI Specification](api/openapi.md)** - Interactive REST API documentation
- **[Protocol Buffers](generated/proto/index.md)** - Proto message definitions

## Architecture

The SDK follows a [proto-first architecture](ARCHITECTURE.md) where Protocol Buffer definitions drive code generation for multiple languages.

## Development

See the [Development Guide](DEVELOPMENT.md) for information on contributing to the SDK.