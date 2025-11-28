# Sonrai Zombie Blaster - Makefile
# Common development tasks

.PHONY: help setup run test test-cov clean lint format security install

# Default target
help:
	@echo "Sonrai Zombie Blaster - Development Commands"
	@echo "============================================="
	@echo ""
	@echo "Setup:"
	@echo "  make setup       - One-command setup (venv, deps, .env)"
	@echo "  make install     - Install/update dependencies"
	@echo ""
	@echo "Run:"
	@echo "  make run         - Run the game"
	@echo "  make test        - Run all tests"
	@echo "  make test-cov    - Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint        - Run linters (pylint, mypy)"
	@echo "  make format      - Format code (black, isort)"
	@echo "  make security    - Run security scans"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean       - Remove cache files"
	@echo "  make clean-all   - Remove cache and venv"
	@echo ""

# Setup
setup:
	@./setup.sh

install:
	@echo "📦 Installing dependencies..."
	@pip install -r requirements.txt
	@echo "✅ Dependencies installed"

# Run
run:
	@echo "🎮 Starting Sonrai Zombie Blaster..."
	@python3 src/main.py

# Testing
test:
	@echo "🧪 Running tests..."
	@pytest tests/ -v

test-cov:
	@echo "🧪 Running tests with coverage..."
	@pytest tests/ -v --cov=src --cov-report=html --cov-report=term
	@echo "📊 Coverage report: htmlcov/index.html"

test-unit:
	@echo "🧪 Running unit tests..."
	@pytest tests/unit/ -v

test-integration:
	@echo "🧪 Running integration tests..."
	@pytest tests/integration/ -v

# Code Quality
lint:
	@echo "🔍 Running linters..."
	@echo "  → pylint..."
	@pylint src/ || true
	@echo "  → mypy..."
	@mypy src/ --ignore-missing-imports || true
	@echo "✅ Linting complete"

format:
	@echo "✨ Formatting code..."
	@echo "  → black..."
	@black src/ tests/ --line-length=100
	@echo "  → isort..."
	@isort src/ tests/ --profile black
	@echo "✅ Formatting complete"

security:
	@echo "🔒 Running security scans..."
	@echo "  → bandit..."
	@bandit -r src/ -c .bandit || true
	@echo "  → gitleaks..."
	@gitleaks detect --no-git || true
	@echo "✅ Security scan complete"

# Maintenance
clean:
	@echo "🧹 Cleaning cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".hypothesis" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@echo "✅ Cache cleaned"

clean-all: clean
	@echo "🧹 Removing virtual environment..."
	@rm -rf venv
	@echo "✅ Full clean complete"

# Development
dev:
	@echo "🔧 Starting development mode..."
	@echo "  → Installing pre-commit hooks..."
	@pre-commit install
	@echo "  → Running tests..."
	@make test
	@echo "✅ Development environment ready"

# Pre-commit
pre-commit:
	@echo "🔍 Running pre-commit checks..."
	@pre-commit run --all-files

# Documentation
docs:
	@echo "📚 Opening documentation..."
	@open README.md || xdg-open README.md || echo "See README.md"

# Quick commands
q: run
t: test
f: format
l: lint
s: security
c: clean
