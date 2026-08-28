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
python_version=$(python --version | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.11"

if (( $(echo "$python_version < $required_version" | bc -l) )); then
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
