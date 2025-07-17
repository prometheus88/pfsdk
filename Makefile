# PostFiat SDK Development Makefile
# 
# Common development tasks for the PostFiat SDK

.PHONY: help proto types tests tests-dynamic tests-core clean install dev-setup ts-build ts-test ts-test-all test bump-version bump-ts-version build-py build-ts docs release deps

# Default target
help:
	@echo "PostFiat SDK Development Commands"
	@echo "================================="
	@echo ""
	@echo "Setup:"
	@echo "  install      Install package in development mode"
	@echo "  dev-setup    Complete development environment setup"
	@echo "  deps         Install all Python and TypeScript dependencies"
	@echo ""
	@echo "Code Generation:"
	@echo "  proto        Generate protobuf classes from .proto files"
	@echo "  types        Generate Python types (enums, exceptions)"
	@echo "  tests        Run all tests (Python + TypeScript, canonical)"
	@echo "  tests-all    Run all generated and manual tests (Python + TypeScript)"
	@echo "  tests-manual Run manual tests only (Python)"
	@echo "  ts-build     Build TypeScript SDK (npm run build)"
	@echo "  ts-test      Run TypeScript tests (npm test)"
	@echo "  ts-test-all  Run all TypeScript unit and integration tests"
	@echo "  test         Alias for 'tests' (run all tests)"
	@echo ""
	@echo "Build & Release:"
	@echo "  build-py     Build Python package(s) (.whl, .tar.gz)"
	@echo "  build-ts     Build TypeScript package(s) (.tgz)"
	@echo "  release      Build all release artifacts (Python + TypeScript)"
	@echo ""
	@echo "Documentation:"
	@echo "  docs         Build all documentation (mkdocs, Sphinx, TypeDoc, Swagger, etc.)"
	@echo ""
	@echo "Version Management:"
	@echo "  bump-version     Update all version strings from VERSION file (Python + TypeScript)"
	@echo "  bump-ts-version  Update TypeScript version strings only"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean        Clean generated files and caches"
	@echo "  regen-all    Regenerate everything (proto + types + tests)"

# Installation and setup
install:
	pip install -e .

dev-setup: install
	@echo "🚀 Setting up PostFiat SDK development environment..."
	@echo "📦 Installing development dependencies..."
	pip install -e ".[dev]"
	@echo "🔧 Generating initial code..."
	$(MAKE) regen-all
	@echo "✅ Development setup complete!"

# Install all dependencies
deps:
	@echo "📦 Installing Python dependencies..."
	pip install -e .
	pip install -e "python/[dev]"
	pip install build twine
	@echo "📦 Upgrading npm to compatible version (for CI rollup bug workaround)..."
	cd typescript && node -e "const v=parseInt(process.versions.node.split('.')[0]); process.exit(v>=20?0:1)" \
	  && npm install -g npm@latest \
	  || npm install -g npm@10
	@echo "📦 Installing TypeScript dependencies..."
	cd typescript && rm -rf node_modules && npm ci
	# If you see rollup native module errors in CI, add an npm upgrade step before this:
	#   npm install -g npm@latest
	# As a last resort, also delete package-lock.json and use npm install (not ci):
	#   rm -rf node_modules package-lock.json && npm install

# Code generation
proto: deps
	@echo "🔄 Generating protobuf classes..."
	cd proto && buf generate --template buf.gen.yaml

types:
	@echo "🔄 Generating Python types..."
	cd python && python scripts/generate_python_types.py

tests-dynamic:
	@echo "🔄 Generating dynamic proto tests..."
	cd python && python scripts/generate_dynamic_protobuf_tests.py

# Testing
# Canonical: run all tests in all languages
tests:
	@echo "🧪 Running manual Python tests..."
	cd python && python -m pytest tests/manual/ -v
	@echo "🧪 Running core dynamic Python tests..."
	cd python && python scripts/dev_test_regen.py --run-tests --core-only
	@echo "🧪 Running all TypeScript unit and integration tests..."
	cd typescript && npm install && npm run test:all
	@echo "✅ All Python and TypeScript tests completed!"

test: tests

# All generated and manual tests (Python + TypeScript)
tests-all:
	@echo "🧪 Running all generated Python tests..."
	cd python && python -m pytest tests/generated/ -v
	@echo "🧪 Running manual Python tests..."
	cd python && python -m pytest tests/manual/ -v
	@echo "🧪 Running all TypeScript unit and integration tests..."
	cd typescript && npm install && npm run test:all
	@echo "✅ All Python and TypeScript tests completed!"

tests-manual:
	@echo "🧪 Running manual tests..."
	cd python && python -m pytest tests/manual/ -v

# TypeScript build and test
ts-build:
	@echo "🔨 Building TypeScript SDK..."
	cd typescript && npm install && npm run build

ts-test:
	@echo "🧪 Running TypeScript tests..."
	cd typescript && npm install && npm test

ts-test-all:
	@echo "🧪 Running all TypeScript unit and integration tests..."
	cd typescript && npm install && npm run test:all

# Unified test target
# test: tests-manual tests-core ts-test-all # This line is now redundant as 'test' is an alias for 'tests'

# Maintenance
clean:
	@echo "🧹 Cleaning generated files and caches..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf tests/generated/*.py 2>/dev/null || true
	@echo "✅ Cleanup complete"

regen-all: proto types tests
	@echo "✅ All code generation complete!"

# CI simulation
ci-check:
	@echo "🔍 Running CI checks locally..."
	python scripts/ci_test_generation.py --validate-only
	python scripts/ci_test_generation.py --force

# Development workflow shortcuts
dev-proto: proto types tests tests-core
	@echo "✅ Proto development workflow complete!"

dev-quick: tests tests-core
	@echo "✅ Quick test regeneration complete!"

# Version bumping
bump-version: proto
	@echo "🔢 Bumping all version strings from VERSION file..."
	./scripts/update-all-versions.sh

bump-ts-version:
	@echo "🔢 Bumping TypeScript version strings from VERSION file..."
	cd typescript && node scripts/update-version.js

# Build Python package(s)
build-py:
	@echo "📦 Building Python package(s)..."
	cd python && python -m build

# Build TypeScript package(s)
build-ts:
	@echo "📦 Building TypeScript package(s)..."
	cd typescript && npm run build && npm pack

# Build all documentation (mkdocs, Sphinx, TypeDoc, Swagger, etc.)
docs:
	@echo "📚 Building documentation..."
	# Python API docs (Sphinx)
	cd python && sphinx-build -b html docs docs/_build/html
	# TypeScript API docs (TypeDoc)
	cd typescript && npx typedoc --out ../docs/generated/typescript src/index.ts --plugin typedoc-plugin-markdown --theme markdown --skipErrorChecking
	# MkDocs site
	mkdocs build
	@echo "✅ Documentation build complete!"

# Build all release artifacts (Python + TypeScript)
release: build-py build-ts
	@echo "🎉 All release artifacts built!"
