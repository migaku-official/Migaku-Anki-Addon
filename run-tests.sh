#!/bin/bash
# Test runner script for Migaku Anki Add-on
# Usage: ./run-tests.sh

set -e

echo "🧪 Running Migaku Anki Add-on Tests"
echo "======================================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed"
    echo "Please install Node.js v14 or higher from https://nodejs.org/"
    exit 1
fi

# Display Node version
NODE_VERSION=$(node --version)
echo "Using Node.js $NODE_VERSION"
echo ""

# Run syntax parser tests
echo "Running syntax-parser tests..."
node tests/syntax-parser.test.js

# Exit with test result
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
    exit 0
else
    echo ""
    echo "❌ Some tests failed"
    exit 1
fi
