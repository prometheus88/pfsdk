#!/bin/bash

# PostFiat SDK: Setup A2A Proto Dependency
# This script sets up the A2A project as a git submodule for proto dependencies

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
A2A_SUBMODULE_PATH="$REPO_ROOT/third_party/a2a"

echo "🔧 Setting up A2A proto dependency for PostFiat SDK..."

# Create third_party directory if it doesn't exist
mkdir -p "$REPO_ROOT/third_party"

# Add A2A as git submodule if not already present
if [ ! -d "$A2A_SUBMODULE_PATH" ]; then
    echo "📦 Adding A2A project as git submodule..."
    cd "$REPO_ROOT"
    # Check if submodule is already configured in .gitmodules
    if git config --file .gitmodules --get-regexp path | grep -q "third_party/a2a"; then
        echo "🔄 Submodule configured but directory missing, initializing..."
        git submodule update --init --recursive
    else
        echo "➕ Adding new submodule..."
        git submodule add https://github.com/a2aproject/A2A.git third_party/a2a
        git submodule update --init --recursive
    fi
else
    echo "✅ A2A submodule already exists"
    # In CI, submodule is already checked out, so just verify it's there
    if [ -f "$A2A_SUBMODULE_PATH/specification/grpc/a2a.proto" ]; then
        echo "✅ A2A proto file found"
    else
        echo "⚠️ A2A proto file missing, updating submodule..."
        cd "$REPO_ROOT"
        git submodule update --init --recursive
    fi
fi

# Create directory structure for A2A proto imports
A2A_PROTO_DIR="$REPO_ROOT/proto/a2a/v1"
if [ ! -d "$A2A_PROTO_DIR" ]; then
    echo "🔗 Creating directory structure for A2A proto imports..."
    mkdir -p "$A2A_PROTO_DIR"
    cd "$A2A_PROTO_DIR"
    ln -sf "../../../third_party/a2a/specification/grpc/a2a.proto" "a2a.proto"
else
    echo "✅ A2A proto directory structure already exists"
fi

# Update buf dependencies
echo "📋 Updating buf dependencies..."
cd "$REPO_ROOT/proto"
buf dep update

echo "✅ A2A dependency setup complete!"
echo ""
echo "Next steps:"
echo "1. Run 'buf generate' to generate code with A2A integration"
echo "2. Commit the submodule and buf.lock changes"
echo "3. Update your imports to use A2A types where appropriate"
