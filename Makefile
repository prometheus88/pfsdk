# PostFiat SDK Development Makefile
# 
# Common development tasks for the PostFiat SDK

.PHONY: help proto types tests tests-dynamic tests-core clean install dev-setup

# Default target
help:
	@echo "PostFiat SDK Development Commands"
	@echo "================================="
	@echo ""
	@echo "Setup:"
	@echo "  install      Install package in development mode"
	@echo "  dev-setup    Complete development environment setup"
	@echo ""
	@echo "Code Generation:"
	@echo "  proto        Generate protobuf classes from .proto files"
	@echo "  types        Generate Python types (enums, exceptions)"
	@echo "  tests        Generate dynamic proto tests (recommended)"
	@echo ""
	@echo "Testing:"
	@echo "  tests-core   Run core dynamic tests (known to work)"
	@echo "  tests-all    Run all generated tests"
	@echo "  tests-manual Run manual tests only"
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

# Code generation
proto:
	@echo "🔄 Generating protobuf classes..."
	cd proto && buf generate --template buf.gen.yaml

types:
	@echo "🔄 Generating Python types..."
	python scripts/generate_python_types.py

tests:
	@echo "🔄 Generating dynamic proto tests..."
	python scripts/generate_dynamic_protobuf_tests.py

# Testing
tests-core:
	@echo "🧪 Running core dynamic tests..."
	python scripts/dev_test_regen.py --run-tests --core-only

tests-all:
	@echo "🧪 Running all generated tests..."
	python -m pytest tests/generated/ -v

tests-manual:
	@echo "🧪 Running manual tests..."
	python -m pytest tests/manual/ -v

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
