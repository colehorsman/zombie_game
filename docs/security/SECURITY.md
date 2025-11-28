# Security Guide - Sonrai Zombie Blaster

**Last Updated:** November 28, 2024
**Security Agent Review**

---

## Overview

This document outlines security best practices, credential management, and security procedures for Sonrai Zombie Blaster.

---

## Table of Contents

1. [Credential Management](#credential-management)
2. [API Token Rotation](#api-token-rotation)
3. [Secret Storage](#secret-storage)
4. [Security Scanning](#security-scanning)
5. [Incident Response](#incident-response)

---

## Credential Management

### API Token Security

**Current Practice:**
- ✅ Daily token rotation (24-hour token lifetime)
- ✅ Tokens stored in `.env` file (never committed)
- ✅ Separate tokens for dev/staging/production
- ✅ Manual rotation via Sonrai API (takes ~1 minute)

**Token Types:**
- **Development:** 24-hour tokens, rotated daily
- **Demo/Staging:** 24-hour tokens, rotated daily
- **Production:** 24-hour tokens, rotated daily

### Why Daily Rotation?

**Benefits:**
1. **Minimal exposure window** - If token leaked, only valid for 24 hours
2. **Audit trail** - Daily rotation creates clear audit log
3. **Best practice** - Exceeds industry standard (90-day rotation)
4. **Low overhead** - Takes ~1 minute per day
5. **Automated expiry** - Tokens automatically expire, no manual revocation needed

**Risk Mitigation:**
- Compromised token only valid for remaining hours in 24-hour window
- Daily rotation prevents long-term unauthorized access
- Forces regular credential hygiene

---

## API Token Rotation

### Manual Rotation Process (Current)

**Frequency:** Daily (every 24 hours)
**Time Required:** ~1 minute
**Method:** Sonrai API token generation

**Steps:**

1. **Generate New Token**
   ```bash
   # Log into Sonrai platform
   # Navigate to: Settings → API Tokens
   # Click "Generate New Token"
   # Set expiration: 24 hours
   # Copy token to clipboard
   ```

2. **Update .env File**
   ```bash
   # Edit .env
   nano .env

   # Update SONRAI_API_TOKEN
   SONRAI_API_TOKEN=<new-token-here>

   # Save and exit
   ```

3. **Test Connectivity**
   ```bash
   # Quick test
   python3 -c "from src.sonrai_client import SonraiAPIClient; \
               import os; from dotenv import load_dotenv; \
               load_dotenv(); \
               client = SonraiAPIClient(os.getenv('SONRAI_API_URL'), \
                                       os.getenv('SONRAI_ORG_ID'), \
                                       os.getenv('SONRAI_API_TOKEN')); \
               print('✅ Token valid' if client.authenticate() else '❌ Token invalid')"
   ```

4. **Document Rotation**
   ```bash
   # Optional: Log rotation date
   echo "Token rotated: $(date)" >> .token_rotation_log
   ```

**Total Time:** ~1 minute

### Future Automation (Optional)

**Potential Automation:**
```bash
#!/bin/bash
# rotate_token.sh (future enhancement)

# Generate new token via Sonrai API
NEW_TOKEN=$(curl -X POST https://api.sonraisecurity.com/tokens \
  -H "Authorization: Bearer $CURRENT_TOKEN" \
  -d '{"expiration": "24h"}' | jq -r '.token')

# Update .env file
sed -i '' "s/SONRAI_API_TOKEN=.*/SONRAI_API_TOKEN=$NEW_TOKEN/" .env

# Test new token
python3 -c "from src.sonrai_client import SonraiAPIClient; ..."

echo "✅ Token rotated successfully"
```

**Note:** Manual rotation is currently preferred for:
- Explicit control over token generation
- Immediate awareness of rotation
- Simple process (1 minute)
- No automation complexity

---

## Secret Storage

### Environment Variables

**Required Secrets:**
```bash
# .env (NEVER commit to git)
SONRAI_API_URL=https://your-org.sonraisecurity.com/graphql
SONRAI_ORG_ID=your_organization_id
SONRAI_API_TOKEN=your_24_hour_token
```

**Storage Rules:**
- ✅ Store in `.env` file
- ✅ `.env` in `.gitignore`
- ✅ Use `.env.example` for templates (no real values)
- ❌ Never commit `.env` to git
- ❌ Never hardcode secrets in code
- ❌ Never log secrets (even in debug mode)

### .env.example Template

```bash
# Sonrai API Configuration
SONRAI_API_URL=https://your-org.sonraisecurity.com/graphql
SONRAI_ORG_ID=your_organization_id
SONRAI_API_TOKEN=your_api_token_here

# Game Configuration
GAME_WIDTH=1280
GAME_HEIGHT=720
FULLSCREEN=false
TARGET_FPS=60
MAX_ZOMBIES=1000
```

### Secret Validation

**On Startup:**
```python
# src/main.py validates required secrets
required_vars = ['SONRAI_API_URL', 'SONRAI_ORG_ID', 'SONRAI_API_TOKEN']
missing = [var for var in required_vars if not os.getenv(var)]
if missing:
    raise ValueError(f"Missing required environment variables: {missing}")
```

---

## Security Scanning

### Pre-Commit Hooks

**Automated Scans:**
```bash
# Runs on every commit
pre-commit run --all-files
```

**Scans Include:**
1. **Gitleaks** - Secret detection
2. **Bandit** - Python security issues (SAST)
3. **Semgrep** - Security patterns
4. **Black** - Code formatting
5. **Pylint** - Code quality
6. **Mypy** - Type checking

### Manual Security Scans

**Run Security Scans:**
```bash
# Bandit (SAST)
bandit -r src/ -c .bandit

# Gitleaks (secrets)
gitleaks detect --no-git

# Semgrep (patterns)
semgrep --config auto src/
```

**Expected Results:**
- ✅ No secrets detected
- ✅ No high/medium severity issues
- ✅ All scans passing

### Security Scan Schedule

**Frequency:**
- **Every commit:** Automated via pre-commit hooks
- **Daily:** Manual scan during development
- **Before deployment:** Full security audit
- **Before submission:** Comprehensive scan

---

## Incident Response

### Token Compromise

**If token is compromised:**

1. **Immediate Actions (< 5 minutes)**
   ```bash
   # 1. Generate new token immediately
   # 2. Update .env with new token
   # 3. Test new token works
   # 4. Old token auto-expires in < 24 hours
   ```

2. **Verification**
   ```bash
   # Verify new token works
   python3 src/main.py

   # Check API connectivity
   # Verify game loads zombies
   ```

3. **Documentation**
   ```bash
   # Log incident
   echo "$(date): Token compromised and rotated" >> .security_incidents.log
   ```

4. **Review**
   - How was token compromised?
   - Update procedures to prevent recurrence
   - Consider additional security measures

**Recovery Time:** < 5 minutes (due to daily rotation practice)

### Secret Exposure in Git

**If secret committed to git:**

1. **Immediate Actions**
   ```bash
   # 1. Rotate token immediately (new 24-hour token)
   # 2. Remove secret from git history
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all

   # 3. Force push (if necessary)
   git push origin --force --all
   ```

2. **Prevention**
   - Verify `.env` in `.gitignore`
   - Run `gitleaks detect` before push
   - Use pre-commit hooks

### API Abuse Detection

**Signs of abuse:**
- Unusual API call patterns
- High error rates
- Unexpected geographic locations
- Off-hours activity

**Response:**
1. Rotate token immediately
2. Review API logs in Sonrai platform
3. Investigate source of abuse
4. Update security procedures

---

## Security Best Practices

### Do's

✅ **Rotate tokens daily** (24-hour lifetime)
✅ **Use `.env` for secrets** (never commit)
✅ **Run security scans** (pre-commit hooks)
✅ **Test token after rotation** (verify connectivity)
✅ **Use separate tokens** (dev/staging/production)
✅ **Monitor API usage** (check Sonrai logs)
✅ **Document incidents** (maintain security log)

### Don'ts

❌ **Never commit `.env`** to git
❌ **Never hardcode secrets** in code
❌ **Never log secrets** (even in debug)
❌ **Never share tokens** (use separate tokens)
❌ **Never skip rotation** (daily is critical)
❌ **Never ignore security scans** (fix issues immediately)
❌ **Never use long-lived tokens** (24 hours max)

---

## Security Metrics

### Current Security Posture

**Token Management:**
- ✅ Daily rotation (24-hour tokens)
- ✅ Manual process (1 minute)
- ✅ Separate tokens per environment
- ✅ Automatic expiration

**Secret Storage:**
- ✅ `.env` file (not committed)
- ✅ `.env.example` template
- ✅ No hardcoded secrets
- ✅ Validated on startup

**Security Scanning:**
- ✅ Pre-commit hooks active
- ✅ Gitleaks, Bandit, Semgrep
- ✅ All scans passing
- ✅ No secrets detected

**API Security:**
- ✅ Request timeouts (SEC-002)
- ✅ Exponential backoff retry
- ✅ Error sanitization (SEC-001)
- ✅ Rate limiting (planned)

**Overall Security Score:** 9.5/10 (Architecture Review Board)

---

## Compliance

### Security Standards

**Followed Standards:**
- ✅ OWASP Top 10 (secure coding)
- ✅ CIS Controls (credential management)
- ✅ NIST Cybersecurity Framework
- ✅ Principle of Least Privilege

**Audit Trail:**
- Token rotation: Daily
- Security scans: Every commit
- Incident response: Documented
- Access control: Environment-based

---

## Future Enhancements

### Planned Improvements

1. **Automated Token Rotation** (Optional)
   - Script to rotate tokens automatically
   - Notification on rotation
   - Fallback to manual if automation fails

2. **Secret Management Service** (Production)
   - AWS Secrets Manager
   - HashiCorp Vault
   - Azure Key Vault

3. **Enhanced Monitoring**
   - API usage alerts
   - Anomaly detection
   - Security event logging

4. **Rate Limiting** (SEC-003)
   - Client-side rate limiting
   - Prevent API abuse
   - Graceful degradation

---

## References

- **Security Agent Review:** Architecture Review Board Report
- **API Timeout Strategy:** docs/API_TIMEOUT_STRATEGY.md
- **Deployment Guide:** DEPLOYMENT.md (security section)
- **Sonrai API Docs:** docs/sonrai-api/

---

## Contact

**Security Issues:**
- Email: security@sonraisecurity.com
- GitHub: Open security issue (private)

**Token Issues:**
- Sonrai Support: support@sonraisecurity.com
- Documentation: https://docs.sonraisecurity.com

---

**Maintained By:** Security Agent
**Last Updated:** November 28, 2024
**Next Review:** After Kiroween submission (Dec 5, 2025)
**Token Rotation:** Daily (24-hour tokens)
