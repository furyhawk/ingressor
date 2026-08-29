#!/bin/bash

# Verification script for Marker PDF Converter - Reflex Framework
# This script checks that all necessary files are in place

set -e

echo "🔍 Verifying Reflex Framework Setup..."
echo "======================================"
echo ""

ERRORS=0
WARNINGS=0

# Check Python files
echo "📄 Checking Python files..."
files=(
    "reflex_app.py"
    "marker_converter/marker_converter.py"
    "src/ingressor/__init__.py"
    "src/ingressor/app.py"
    "src/ingressor/components.py"
    "src/ingressor/marker.py"
    "src/ingressor/state.py"
    "rxconfig.py"
    "pyproject.toml"
    "requirements.txt"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (MISSING)"
        ERRORS=$((ERRORS+1))
    fi
done

echo ""

# Check documentation files
echo "📚 Checking documentation..."
docs=(
    "README.md"
    "QUICKSTART.md"
    "MIGRATION_GUIDE.md"
    "DEPLOYMENT.md"
    "SUMMARY.md"
)

for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        echo "  ✅ $doc"
    else
        echo "  ⚠️  $doc (MISSING)"
        WARNINGS=$((WARNINGS+1))
    fi
done

echo ""

# Check configuration files
echo "⚙️  Checking configuration files..."
configs=(
    "Dockerfile"
    "docker-compose.yml"
    ".dockerignore"
    ".env.example"
    "Makefile"
)

for config in "${configs[@]}"; do
    if [ -f "$config" ]; then
        echo "  ✅ $config"
    else
        echo "  ⚠️  $config (MISSING)"
        WARNINGS=$((WARNINGS+1))
    fi
done

echo ""

# Check Python syntax
echo "🐍 Checking Python syntax..."
if python -m py_compile reflex_app.py 2>/dev/null; then
    echo "  ✅ reflex_app.py syntax valid"
else
    echo "  ❌ reflex_app.py has syntax errors"
    ERRORS=$((ERRORS+1))
fi

if python -m py_compile marker_converter/marker_converter.py src/ingressor/*.py 2>/dev/null; then
    echo "  ✅ package entrypoints syntax valid"
else
    echo "  ❌ package entrypoints have syntax errors"
    ERRORS=$((ERRORS+1))
fi

if python -m py_compile rxconfig.py 2>/dev/null; then
    echo "  ✅ rxconfig.py syntax valid"
else
    echo "  ❌ rxconfig.py has syntax errors"
    ERRORS=$((ERRORS+1))
fi

echo ""

# Check if git is initialized
echo "🔗 Checking git setup..."
if [ -d ".git" ]; then
    echo "  ✅ Git repository initialized"
else
    echo "  ⚠️  Git repository not initialized"
    WARNINGS=$((WARNINGS+1))
fi

echo ""

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
required="3.11"
if [[ "$python_version" == 3.1[1-9]* ]] || [[ "$python_version" == 3.[2-9][0-9]* ]]; then
    echo "  ✅ Python version: $python_version (meets requirement >= 3.11)"
else
    echo "  ⚠️  Python version: $python_version (recommend 3.11+)"
    WARNINGS=$((WARNINGS+1))
fi

echo ""

# Summary
echo "======================================"
echo "📊 Verification Summary"
echo "======================================"
echo "  Errors:   $ERRORS"
echo "  Warnings: $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo "✅ All checks passed! Setup is complete."
        echo ""
        echo "Next steps:"
        echo "  1. Install dependencies: uv sync (or pip install -e .)"
        echo "  2. Run the app: reflex run (or make run)"
        echo "  3. Open: http://localhost:3000"
        echo ""
        exit 0
    else
        echo "✅ Setup is complete with minor warnings."
        echo ""
        echo "Next steps:"
        echo "  1. Install dependencies: uv sync (or pip install -e .)"
        echo "  2. Run the app: reflex run (or make run)"
        echo "  3. Open: http://localhost:3000"
        echo ""
        exit 0
    fi
else
    echo "❌ Setup has errors. Please fix the issues above."
    exit 1
fi
