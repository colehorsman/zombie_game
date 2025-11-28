# API Timeout Strategy

**Implemented:** SEC-002
**Date:** November 28, 2024
**Security Agent Review**

---

## Overview

This document describes the timeout and retry strategy for all Sonrai API calls, ensuring the game remains responsive even when the API is slow or unavailable.

---

## Timeout Configuration

### Timeout Values

```python
API_TIMEOUT_SHORT = 10      # Quick operations (auth, health checks)
API_TIMEOUT_STANDARD = 30   # Standard queries (fetch data)
API_TIMEOUT_MUTATION = 15   # Mutations (quarantine, block)
```

### Rationale

**Short Timeout (10s):**
- Used for: Authentication, health checks
- Why: These should be fast; if they're slow, something is wrong
- Impact: Fails fast, allows quick retry or fallback

**Standard Timeout (30s):**
- Used for: Fetching zombies, third parties, exemptions, accounts
- Why: Large data sets may take time to query
- Impact: Balances responsiveness with data completeness

**Mutation Timeout (15s):**
- Used for: Quarantine, block operations, JIT protection
- Why: Write operations should be faster than reads
- Impact: Ensures timely feedback to player actions

---

## Retry Strategy

### Configuration

```python
API_MAX_RETRIES = 3         # Maximum retry attempts
API_RETRY_DELAY = 1.0       # Initial delay (seconds)
```

### Exponential Backoff

Retry delays increase exponentially:
- Attempt 1: Immediate
- Attempt 2: 1 second delay
- Attempt 3: 2 second delay
- Attempt 4: 4 second delay (if max_retries increased)

### When to Retry

**Retry on:**
- ✅ Timeout errors (`requests.exceptions.Timeout`)
- ✅ Connection errors (`requests.exceptions.ConnectionError`)
- ✅ Temporary server errors (5xx status codes)

**Don't retry on:**
- ❌ Authentication errors (401)
- ❌ Authorization errors (403)
- ❌ Not found errors (404)
- ❌ Client errors (4xx except 429)

---

## Implementation

### Helper Method

All API calls use `_make_request_with_timeout()`:

```python
def _make_request_with_timeout(
    self,
    query: str,
    variables: Dict[str, Any] = None,
    timeout: int = API_TIMEOUT_STANDARD,
    max_retries: int = API_MAX_RETRIES,
) -> Dict[str, Any]:
    """Make API request with timeout and retry logic."""
    # Implements exponential backoff retry
    # Logs all attempts and failures
    # Raises exception after all retries exhausted
```

### Usage Example

```python
# Fetch data with standard timeout
response = self._make_request_with_timeout(
    query=my_query,
    variables=my_vars,
    timeout=API_TIMEOUT_STANDARD
)

# Quick operation with short timeout
response = self._make_request_with_timeout(
    query=auth_query,
    timeout=API_TIMEOUT_SHORT
)

# Mutation with mutation timeout
response = self._make_request_with_timeout(
    query=quarantine_mutation,
    variables=mutation_vars,
    timeout=API_TIMEOUT_MUTATION
)
```

---

## Error Handling

### Timeout Errors

**What happens:**
1. Request times out after configured seconds
2. Logged as warning with attempt number
3. Exponential backoff delay
4. Retry up to max_retries times
5. If all retries fail, raise exception

**User Experience:**
- Game continues running (doesn't freeze)
- Error logged to console
- Graceful degradation (empty data returned)
- User sees "Unable to load data" message

### Network Errors

**What happens:**
1. Connection fails (network down, DNS failure, etc.)
2. Same retry logic as timeouts
3. Logged with details
4. Graceful fallback

**User Experience:**
- Game remains playable
- Offline mode (if implemented)
- Clear error message

---

## Monitoring

### Logging

All timeout and retry events are logged:

```
WARNING: API request timeout (attempt 1/3): HTTPSConnectionPool...
INFO: Retrying in 1.0s...
WARNING: API request timeout (attempt 2/3): HTTPSConnectionPool...
INFO: Retrying in 2.0s...
ERROR: API request failed after 3 attempts
```

### Metrics to Track

- Total API calls
- Timeout rate (%)
- Retry rate (%)
- Average response time
- Success rate after retries

---

## Testing

### Manual Testing

```bash
# Test with slow API (simulate with network throttling)
# Game should remain responsive

# Test with API down
# Game should fail gracefully

# Test with intermittent connectivity
# Retries should succeed
```

### Automated Testing

```python
def test_api_timeout():
    """Test that API calls timeout appropriately."""
    # Mock slow API response
    # Verify timeout occurs
    # Verify retry logic

def test_api_retry():
    """Test retry logic with exponential backoff."""
    # Mock failing API
    # Verify retries occur
    # Verify backoff delays
```

---

## Performance Impact

### Before (No Timeouts)

**Problem:**
- Hanging requests could freeze game indefinitely
- No way to recover from slow API
- Poor user experience

**Metrics:**
- Worst case: Infinite hang
- User frustration: High

### After (With Timeouts)

**Solution:**
- Maximum wait: 30s + retries = ~60s worst case
- Game remains responsive
- Clear feedback to user

**Metrics:**
- Worst case: 60s before failure
- User frustration: Low (knows what's happening)

---

## Configuration

### Environment Variables

Future enhancement - make timeouts configurable:

```bash
# .env
SONRAI_API_TIMEOUT_SHORT=10
SONRAI_API_TIMEOUT_STANDARD=30
SONRAI_API_TIMEOUT_MUTATION=15
SONRAI_API_MAX_RETRIES=3
```

### Per-Environment Settings

**Development:**
- Shorter timeouts (faster feedback)
- More verbose logging

**Production:**
- Standard timeouts
- INFO level logging

**Demo:**
- Shorter timeouts (responsive demos)
- Minimal logging

---

## Best Practices

### Do's

✅ Always specify timeout for API calls
✅ Use appropriate timeout for operation type
✅ Log timeout events for monitoring
✅ Implement retry with exponential backoff
✅ Provide user feedback on failures
✅ Test with slow/failing API

### Don'ts

❌ Never make API calls without timeout
❌ Don't use same timeout for all operations
❌ Don't retry indefinitely
❌ Don't hide timeout errors from logs
❌ Don't freeze UI during API calls
❌ Don't assume API is always fast

---

## Future Enhancements

### Planned Improvements

1. **Circuit Breaker Pattern**
   - Stop calling failing API temporarily
   - Automatic recovery when API healthy

2. **Request Queuing**
   - Queue API calls during high load
   - Process when API available

3. **Caching**
   - Cache API responses
   - Reduce API call frequency

4. **Offline Mode**
   - Continue gameplay without API
   - Sync when connection restored

5. **Health Monitoring**
   - Track API health metrics
   - Alert on degradation

---

## References

- **Security Agent Review:** Timeout strategy prevents DoS
- **Operations Agent Review:** Monitoring and alerting
- **Architecture Agent Review:** Error handling patterns
- **Sonrai Agent Review:** API best practices

---

**Maintained By:** Security Agent
**Last Updated:** November 28, 2024
**Next Review:** After production deployment
