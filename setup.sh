#!/bin/bash
# Sonrai Zombie Blaster - One-Command Setup Script
# Usage: ./setup.sh

set -e  # Exit on error

echo "🎮 Sonrai Zombie Blaster - Setup Script"
echo "========================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.11"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
    echo "❌ Python 3.11+ required. Found: $PYTHON_VERSION"
    echo "   Please install Python 3.11 or higher"
    exit 1
fi
echo "✅ Python $PYTHON_VERSION"
echo ""

# Create virtual environment
echo "🔧 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "   Virtual environment already exists"
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip --quiet
echo "✅ pip upgraded"
echo ""

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt --quiet
echo "✅ Dependencies installed"
echo ""

# Setup environment file
echo "⚙️  Setting up environment configuration..."
if [ -f ".env" ]; then
    echo "   .env file already exists"
else
    cp .env.example .env
    echo "✅ .env file created from template"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env with your Sonrai credentials:"
    echo "   - SONRAI_API_URL"
    echo "   - SONRAI_ORG_ID"
    echo "   - SONRAI_API_TOKEN"
    echo ""
fi

# Install pre-commit hooks
echo "🔒 Installing pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install --quiet
    echo "✅ Pre-commit hooks installed"
else
    echo "⚠️  pre-commit not found. Install with: pip install pre-commit"
fi
echo ""

# Verify installation
echo "🧪 Verifying installation..."
python3 -c "import pygame; import requests; import dotenv" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Core dependencies verified"
else
    echo "❌ Dependency verification failed"
    exit 1
fi
echo ""

# Success message
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Edit .env with your Sonrai credentials"
echo "   2. Run the game: python3 src/main.py"
echo "   3. Run tests: pytest tests/ -v"
echo ""
echo "📚 Documentation:"
echo "   - Quick start: CONTRIBUTING.md"
echo "   - Troubleshooting: TROUBLESHOOTING.md"
echo "   - Deployment: DEPLOYMENT.md"
echo ""
echo "🎮 Happy coding!"
