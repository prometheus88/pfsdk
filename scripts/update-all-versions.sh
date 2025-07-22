#!/bin/bash
set -e

echo "🚀 Updating all package versions from centralized VERSION file..."

# Check if VERSION file exists
if [ ! -f "VERSION" ]; then
    echo "❌ VERSION file not found!"
    exit 1
fi

VERSION=$(cat VERSION)
echo "📦 Version: $VERSION"

echo ""
echo "🐍 Updating Python packages..."
cd python
python3 scripts/generate_python_types.py
echo "✅ Python versions updated"

echo ""
echo "📘 Updating TypeScript packages..."
cd ../typescript
npm run update-version
echo "✅ TypeScript versions updated"

echo ""
echo "⚡ Updating Solidity packages..."
cd ../solidity
# Update package.json version
node -e "const pkg = require('./package.json'); pkg.version = process.argv[1]; require('fs').writeFileSync('./package.json', JSON.stringify(pkg, null, 2) + '\n');" "$VERSION"
echo "✅ Solidity versions updated"

echo ""
echo "🎉 All versions updated to $VERSION!"
echo ""
echo "📋 Summary:"
echo "  - Centralized VERSION file: $VERSION"
echo "  - Python pyproject.toml: dynamic version from setup.py"
echo "  - Python __init__.py: $VERSION"
echo "  - TypeScript package.json: $VERSION"
echo "  - TypeScript index.ts: $VERSION"
echo "  - TypeScript User-Agent: $VERSION"
echo "  - Solidity package.json: $VERSION"