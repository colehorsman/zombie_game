#!/bin/bash
# Comprehensive security scanning script
# Runs SAST, dependency scanning, and secret detection
# Author: Cole & Kiro

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Zombie Game Security Scan Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Track overall result
OVERALL_RESULT=0

# Function to print section headers
print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. BANDIT - Python SAST
print_header "1/5: Bandit (Python SAST)"
if command_exists bandit; then
    if bandit -r src/ -f json -o reports/bandit_report.json --config .bandit; then
        echo -e "${GREEN}✓ Bandit scan passed!${NC}"
    else
        echo -e "${RED}✗ Bandit found security issues!${NC}"
        echo -e "${YELLOW}View report: reports/bandit_report.json${NC}"
        OVERALL_RESULT=1
    fi
else
    echo -e "${YELLOW}⚠ Bandit not installed. Install with: pip3 install bandit${NC}"
fi

# 2. SEMGREP - Advanced SAST
print_header "2/5: Semgrep (Advanced SAST)"
if command_exists semgrep; then
    if semgrep --config=.semgrep.yml --config=p/python --config=p/security-audit \
        --json --output=reports/semgrep_report.json src/; then
        echo -e "${GREEN}✓ Semgrep scan passed!${NC}"
    else
        echo -e "${RED}✗ Semgrep found security issues!${NC}"
        echo -e "${YELLOW}View report: reports/semgrep_report.json${NC}"
        OVERALL_RESULT=1
    fi
else
    echo -e "${YELLOW}⚠ Semgrep not installed. Install with: pip3 install semgrep${NC}"
fi

# 3. SAFETY - Dependency vulnerability scanning
print_header "3/5: Safety (Dependency Vulnerabilities)"
if command_exists safety; then
    if safety check --json --output reports/safety_report.json; then
        echo -e "${GREEN}✓ No known vulnerabilities in dependencies!${NC}"
    else
        echo -e "${RED}✗ Vulnerable dependencies found!${NC}"
        echo -e "${YELLOW}View report: reports/safety_report.json${NC}"
        OVERALL_RESULT=1
    fi
else
    echo -e "${YELLOW}⚠ Safety not installed. Install with: pip3 install safety${NC}"
fi

# 4. PIP-AUDIT - PyPA official dependency scanner
print_header "4/5: pip-audit (PyPA Dependency Scanner)"
if command_exists pip-audit; then
    if pip-audit --desc --format json --output reports/pip_audit_report.json; then
        echo -e "${GREEN}✓ No vulnerable dependencies found!${NC}"
    else
        echo -e "${RED}✗ Vulnerable dependencies detected!${NC}"
        echo -e "${YELLOW}View report: reports/pip_audit_report.json${NC}"
        OVERALL_RESULT=1
    fi
else
    echo -e "${YELLOW}⚠ pip-audit not installed. Install with: pip3 install pip-audit${NC}"
fi

# 5. GITLEAKS - Secret detection
print_header "5/5: Gitleaks (Secret Detection)"
if command_exists gitleaks; then
    if gitleaks detect --config .gitleaks.toml --report-path reports/gitleaks_report.json --no-git; then
        echo -e "${GREEN}✓ No secrets detected!${NC}"
    else
        echo -e "${RED}✗ Potential secrets found!${NC}"
        echo -e "${YELLOW}View report: reports/gitleaks_report.json${NC}"
        OVERALL_RESULT=1
    fi
else
    echo -e "${YELLOW}⚠ Gitleaks not installed. Install with: brew install gitleaks${NC}"
fi

# Summary
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  Security Scan Summary${NC}"
echo -e "${BLUE}========================================${NC}\n"

if [ $OVERALL_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ All security scans passed!${NC}\n"
else
    echo -e "${RED}✗ Security issues detected. Review reports in ./reports/${NC}\n"
    exit 1
fi
