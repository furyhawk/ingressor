#!/bin/bash

# Marker PDF Converter - Reflex App Launcher
# This script sets up and runs the Reflex application

set -e

echo "🚀 Marker PDF Converter - Reflex Framework"
echo "==========================================="

# Check if Reflex is installed
if ! command -v reflex &> /dev/null; then
    echo "❌ Reflex not found. Installing..."
    pip install reflex>=0.3.0
fi

# Check Python version
python_version=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
if ! python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)"; then
    echo "❌ Python 3.11 or higher is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip install -q -e .

# Run the Reflex app
echo "🌐 Starting Reflex development server..."
echo "📍 Application will be available at http://localhost:3000"
echo ""

reflex run
