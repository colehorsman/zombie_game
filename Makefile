# Zombie Game - Development & Security Makefile
# Author: Cole & Kiro

.PHONY: help install test security clean run lint format

# Default target - show help
help:
	@echo "Zombie Game - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  make install       Install all dependencies"
	@echo "  make run           Run the game"
	@echo "  make test          Run all tests"
	@echo "  make lint          Run code linters"
	@echo "  make format        Format code with black"
	@echo ""
	@echo "Security:"
	@echo "  make security      Run comprehensive security scan"
	@echo "  make sast          Run SAST scanners (Bandit + Semgrep)"
	@echo "  make deps-scan     Scan dependencies for vulnerabilities"
	@echo "  make secrets       Detect hardcoded secrets"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean         Remove temporary files and reports"
	@echo ""

# Install dependencies
install:
	pip3 install -r requirements.txt
	pip3 install --upgrade bandit semgrep safety pip-audit black pylint pytest

# Run the game
run:
	python3 src/main.py

# Run all tests
test:
	python3 -m pytest tests/ -v

# Run comprehensive security scan
security:
	@echo "Running comprehensive security scan..."
	@mkdir -p reports
	@./scripts/security_scan.sh

# Run SAST scanners
sast:
	@echo "Running SAST scanners..."
	@mkdir -p reports
	@echo "→ Bandit (Python SAST)..."
	@bandit -r src/ -f json -o reports/bandit.json --config .bandit || true
	@echo "→ Semgrep (Advanced SAST)..."
	@semgrep --config=.semgrep.yml --config=p/python src/ || true

# Scan dependencies
deps-scan:
	@echo "Scanning dependencies for vulnerabilities..."
	@mkdir -p reports
	@echo "→ Safety check..."
	@safety check --json --output reports/safety.json || true
	@echo "→ pip-audit check..."
	@pip-audit --desc --format json --output reports/pip-audit.json || true

# Detect secrets
secrets:
	@echo "Scanning for hardcoded secrets..."
	@mkdir -p reports
	@if command -v gitleaks >/dev/null 2>&1; then \
		gitleaks detect --config .gitleaks.toml --report-path reports/gitleaks.json --no-git; \
	else \
		echo "Gitleaks not installed. Install with: brew install gitleaks"; \
	fi

# Lint code
lint:
	@echo "Running linters..."
	@pylint src/ --rcfile=.pylintrc || true
	@bandit -r src/ --config .bandit || true

# Format code
format:
	@echo "Formatting code with black..."
	@black src/ tests/

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .pytest_cache build/ dist/ *.egg-info
	@echo "Clean complete!"
