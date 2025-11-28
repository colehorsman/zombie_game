# Security Scanning Documentation

This document describes the security scanning tools and processes for the Zombie Game project.

## Overview

The project uses a comprehensive security scanning suite that includes:

1. **SAST (Static Application Security Testing)** - Code analysis
2. **Dependency Scanning** - Vulnerability detection in dependencies
3. **Secret Detection** - Hardcoded credentials/tokens
4. **CI/CD Integration** - Automated scanning in GitHub Actions

## Security Tools

### 1. Bandit (Python SAST)

**Purpose**: Detects common security issues in Python code
**Installation**: `pip3 install bandit`
**Configuration**: `.bandit`
**Usage**: `make sast` or `bandit -r src/`

**What it detects**:
- Hardcoded passwords/secrets
- SQL injection vulnerabilities
- Use of insecure functions (eval, exec, etc.)
- Weak cryptography
- Unsafe deserialization

### 2. Semgrep (Advanced SAST)

**Purpose**: Advanced pattern-based code analysis
**Installation**: `pip3 install semgrep`
**Configuration**: `.semgrep.yml`
**Usage**: `make sast` or `semgrep --config=.semgrep.yml src/`

**What it detects**:
- Command injection
- Path traversal
- Insecure random number generation
- Missing timeouts in HTTP requests
- Dangerous eval/exec usage
- Custom security patterns

### 3. Safety (Dependency Scanner)

**Purpose**: Checks Python dependencies for known vulnerabilities
**Installation**: `pip3 install safety`
**Usage**: `make deps-scan` or `safety check`

**What it detects**:
- CVEs in installed packages
- Known vulnerabilities in transitive dependencies
- Outdated packages with security fixes

### 4. pip-audit (PyPA Official Scanner)

**Purpose**: Official Python Package Authority dependency scanner
**Installation**: `pip3 install pip-audit`
**Usage**: `make deps-scan` or `pip-audit`

**What it detects**:
- Vulnerabilities from PyPI Advisory Database
- CVEs and security advisories
- More accurate than Safety for Python-specific issues

### 5. Gitleaks (Secret Detection)

**Purpose**: Detects hardcoded secrets in code and git history
**Installation**: `brew install gitleaks` (Mac) or download from GitHub
**Configuration**: `.gitleaks.toml`
**Usage**: `make secrets` or `gitleaks detect`

**What it detects**:
- API keys (AWS, GitHub, generic)
- Bearer tokens
- Private keys (RSA, DSA, EC)
- Passwords in code
- Hardcoded credentials

## Running Security Scans

### Quick Start

```bash
# Install all security tools
make install

# Run comprehensive security scan
make security

# View results
ls reports/
```

### Individual Scans

```bash
# SAST only
make sast

# Dependency scan only
make deps-scan

# Secret detection only
make secrets
```

### Manual Commands

```bash
# Bandit
bandit -r src/ -f json -o reports/bandit.json --config .bandit

# Semgrep
semgrep --config=.semgrep.yml --config=p/python src/

# Safety
safety check

# pip-audit
pip-audit --desc

# Gitleaks
gitleaks detect --config .gitleaks.toml
```

## CI/CD Integration

Security scans run automatically on:
- Every push to `main`, `develop`, or `feature/*` branches
- Every pull request to `main` or `develop`
- Weekly scheduled scan (Mondays at 9 AM)

### GitHub Actions Workflow

Location: `.github/workflows/security.yml`

The workflow:
1. Runs all SAST scanners (Bandit, Semgrep)
2. Scans dependencies (Safety, pip-audit)
3. Detects secrets (Gitleaks)
4. Uploads SARIF results to GitHub Security tab
5. Stores reports as artifacts (30-day retention)

### Viewing Results

1. **GitHub UI**: Go to "Security" tab → "Code scanning"
2. **Artifacts**: Actions → Select workflow run → Download "security-reports"
3. **Local**: Check `reports/` directory after running scans

## Report Formats

All tools generate JSON reports in the `reports/` directory:

- `bandit.json` - Bandit findings
- `bandit.sarif` - Bandit SARIF format (for GitHub)
- `semgrep.json` - Semgrep findings
- `semgrep.sarif` - Semgrep SARIF format (for GitHub)
- `safety.json` - Dependency vulnerabilities
- `pip-audit.json` - PyPA dependency scan
- `gitleaks.json` - Detected secrets

## Configuration Files

| File | Purpose |
|------|---------|
| `.bandit` | Bandit SAST config |
| `.semgrep.yml` | Semgrep rules |
| `.gitleaks.toml` | Secret detection patterns |
| `Makefile` | Convenient commands |
| `scripts/security_scan.sh` | Comprehensive scan script |

## Interpreting Results

### Severity Levels

- **HIGH**: Fix immediately - critical security issue
- **MEDIUM**: Fix soon - potential vulnerability
- **LOW**: Review - minor issue or false positive

### Common False Positives

1. **Test files with dummy credentials**: Allowlist in configs
2. **Example code snippets**: Add to allowlist
3. **Non-user-facing scripts**: May be acceptable if documented

## Best Practices

1. **Run scans before committing**:
   ```bash
   make security
   ```

2. **Fix HIGH severity issues immediately**

3. **Review MEDIUM issues** - determine if they apply to your use case

4. **Keep dependencies updated**:
   ```bash
   pip3 list --outdated
   pip3 install --upgrade <package>
   ```

5. **Never commit secrets** - use environment variables:
   ```python
   import os
   api_key = os.getenv("API_KEY")  # Good
   api_key = "sk-12345"             # Bad
   ```

6. **Add false positives to allowlists** - don't ignore them silently

## Remediation Examples

### Hardcoded Secret
```python
# Bad
password = "mySecretPassword123"

# Good
import os
password = os.getenv("PASSWORD")
```

### Command Injection
```python
# Bad
os.system(f"ls {user_input}")

# Good
import subprocess
subprocess.run(["ls", user_input], check=True)
```

### Missing Timeout
```python
# Bad
response = requests.get(url)

# Good
response = requests.get(url, timeout=30)
```

## Emergency Response

If secrets are detected in committed code:

1. **Rotate the secret immediately** - consider it compromised
2. **Remove from git history**:
   ```bash
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch path/to/file' \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. **Force push** (coordinate with team):
   ```bash
   git push origin --force --all
   ```
4. **Update documentation** about the incident

## Support

For questions or issues:
1. Check tool documentation (links in this file)
2. Review GitHub Security tab for detailed findings
3. Contact Cole or Kiro

## References

- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Semgrep Docs](https://semgrep.dev/docs/)
- [Safety](https://pyup.io/safety/)
- [pip-audit](https://github.com/pypa/pip-audit)
- [Gitleaks](https://github.com/gitleaks/gitleaks)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
