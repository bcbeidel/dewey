#!/bin/bash
# Setup script for dewey plugin
# This script is automatically run after plugin installation

set -e

echo "🔧 Setting up dewey plugin..."

# Get the directory where this script is located
PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if pip is available
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ Error: pip is not installed. Please install Python 3.9+ and pip."
    exit 1
fi

# Use pip3 if available, otherwise pip
PIP_CMD=$(command -v pip3 || command -v pip)

# Install the package in editable mode
echo "📦 Installing dewey Python package..."
cd "$PLUGIN_DIR"
$PIP_CMD install -e . --quiet

echo "✅ Dewey plugin setup complete!"
echo ""
echo "Available commands:"
echo "  /dewey:analyze  - Analyze context usage"
echo "  /dewey:split    - Split large files"
echo "  /dewey:check    - Check context health"
echo "  /dewey:optimize - Run full optimization"
echo "  /dewey:report   - Generate usage report"
