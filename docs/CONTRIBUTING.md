# Contributing to PostFiat SDK

Thank you for your interest in contributing to the PostFiat SDK! This document outlines our development workflow, branch protection rules, and contribution guidelines.

## 🏗️ Repository Structure

This is a **proto-first SDK** with automated code generation:

```
pfsdk/
├── proto/                          # Protocol buffer definitions
│   ├── postfiat/v3/               # Proto files (source of truth)
│   ├── buf.yaml                   # Buf configuration
│   └── buf.gen.yaml               # Code generation config
├── postfiat/                      # Generated Python SDK
│   ├── v3/                        # Generated protobuf classes (ignored)
│   ├── types/enums.py             # Generated enums (ignored)
│   ├── exceptions.py              # Generated exceptions (ignored)
│   ├── models/                    # Generated models (ignored)
│   ├── managers/                  # Generated managers (ignored)
│   ├── services/                  # Generated services (ignored)
│   └── clients/                   # Generated clients (ignored)
├── scripts/                       # Build and generation scripts
├── tests/
│   ├── manual/                    # Manual tests (committed)
│   └── generated/                 # Auto-generated tests (ignored)
└── .github/workflows/             # CI/CD automation
```

## 🔄 Development Workflow

### Branch Strategy

- **`main`** - Stable releases, managed via PR from dev
- **`dev`** - Development branch with clean source code only

### Branch Protection Rules

Both branches are protected with the following rules:

**Main Branch:**
- ✅ Requires PR with 1 approval
- ✅ Requires all CI checks to pass
- ✅ Prevents direct pushes
- ✅ Prevents force pushes and deletion
- ✅ Enforced on administrators

**Dev Branch:**
- ✅ Requires PR with 1 approval  
- ✅ Requires CI checks to pass
- ✅ More permissive for development

### Release Strategy

We use **git tags with artifacts** for releases:

**Development:**
- Generated files are **ignored** by .gitignore
- Developers run generation scripts locally
- Focus on source code changes

**Releases:**
- Create tags with "release-" prefix (e.g., `release-0.1.0-rc1`)
- CI automatically builds Python (.whl/.tar.gz) and TypeScript (.tgz) packages
- Artifacts attached to GitHub releases for download
- No automatic publishing to npm/PyPI registries

## 🚀 Getting Started

### Prerequisites

- Python 3.10+ 
- Node.js 18+ (for TypeScript SDK)
- [Buf CLI](https://buf.build/docs/installation)
- Git

### Setup

1. **Clone and setup:**
   ```bash
   git clone https://github.com/allenday/pfsdk.git
   cd pfsdk
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .
   ```

2. **Generate code locally:**
   ```bash
   # Generate protobuf classes
   cd proto && buf generate --template buf.gen.yaml && cd ..
   
   # Generate Python types
   python scripts/generate_python_types.py
   
   # Generate TypeScript SDK
   cd typescript && npm ci && npm run generate:types && cd ..
   
   # Generate comprehensive build (optional)
   python scripts/generate_protobuf.py
   
   # Generate tests
   python scripts/generate_dynamic_protobuf_tests.py
   ```

3. **Run tests:**
   ```bash
   pytest tests/ -v
   ```

## 📝 Making Contributions

### 1. Create Feature Branch

```bash
git checkout dev
git pull origin dev
git checkout -b feature/your-feature-name
```

### 2. Make Changes

**For Proto Changes:**
- Edit files in `proto/postfiat/v3/`
- Run generation scripts to test locally
- Do NOT commit generated files

**For Manual Code:**
- Edit source files in appropriate directories
- Add manual tests in `tests/manual/`
- Follow existing code patterns

### 3. Test Your Changes

```bash
# Generate and test locally
python scripts/generate_python_types.py
python scripts/generate_dynamic_protobuf_tests.py
pytest tests/ -v

# Verify package installation
pip install -e .
python -c "import postfiat; print('✅ Package imports successfully')"
```

### 4. Create Pull Request

1. **Push your branch:**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create PR:** `feature/your-feature-name` → `dev`

3. **PR Requirements:**
   - Clear description of changes
   - All CI checks must pass
   - 1 approval required
   - No direct pushes allowed

### 5. After Merge

The CI will automatically:
- Generate all code from your proto changes
- Run comprehensive test suite
- Auto-commit generated files to main branch (when dev → main)

## 🧪 Testing Guidelines

### Manual Tests
- Write in `tests/manual/`
- Test business logic, integration, edge cases
- Committed to git and run in CI

### Generated Tests
- Auto-created from proto definitions
- Test protobuf contracts and serialization
- Ignored by git, regenerated in CI

### Test Execution
```bash
# Run all tests
pytest tests/ -v

# Run only manual tests
pytest tests/manual/ -v

# Run only generated tests
pytest tests/generated/ -v
```

## 🔧 Code Generation

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed information about the code generation process.

## 📋 PR Checklist

- [ ] Changes tested locally
- [ ] Generated code works correctly
- [ ] Manual tests added/updated if needed
- [ ] Proto changes follow existing patterns
- [ ] CI passes all checks
- [ ] Clear commit messages
- [ ] PR description explains changes

## 🆘 Getting Help

- **Issues:** Use GitHub Issues for bugs and feature requests
- **Discussions:** Use GitHub Discussions for questions
- **CI Problems:** Check the Actions tab for detailed logs

## 📜 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain code quality
- Follow existing patterns and conventions

Thank you for contributing to PostFiat SDK! 🚀

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

## 🧪 Running All Tests

- To run all tests (Python + TypeScript):
```bash
make test
```
