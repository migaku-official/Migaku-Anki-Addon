#!/bin/bash
# Install git hooks for Migaku Anki Add-on development
# Run this script after cloning the repository

set -e

echo "📦 Installing git hooks..."
echo ""

# Check if .git directory exists
if [ ! -d ".git" ]; then
    echo "❌ Error: .git directory not found"
    echo "Make sure you're running this from the repository root"
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Copy pre-push hook
if [ -f "hooks/pre-push" ]; then
    cp hooks/pre-push .git/hooks/pre-push
    chmod +x .git/hooks/pre-push
    echo "✅ Installed pre-push hook"
else
    echo "❌ Error: hooks/pre-push not found"
    exit 1
fi

echo ""
echo "🎉 Git hooks installed successfully!"
echo ""
echo "The pre-push hook will now run tests automatically before each push."
echo "If tests fail, the push will be rejected."
echo ""
echo "To bypass the hook (not recommended), use: git push --no-verify"
