# Sonrai MCP Connection Diagnosis for Kiro

## Summary
The Sonrai MCP server at `https://mcp.s.sonraisecurity.com/stage12902075` is rejecting authentication attempts with the error **"Jwt issuer is not configured"**. This appears to be a server-side JWT validation configuration issue.

## What We Tried

### 1. Manual Bearer Token Authentication
We attempted to connect using the same JWT token that successfully works with the Sonrai GraphQL API:

```bash
curl -H "Authorization: Bearer <token>" \
  "https://mcp.s.sonraisecurity.com/stage12902075"
```

**Result:** `Jwt issuer is not configured`

### 2. JWT Token Analysis
The JWT token contains:
- **Issuer:** "Sonrai"
- **Audience:** "crc-graphql-server.sonraisecurity.com"
- **Org ID:** crc12185275
- **Environment:** crc
- **Scopes:** read:data, read:platform, arrival:upload
- **Expiration:** December 24, 2025 (valid)

This token works perfectly for:
- GraphQL API: `https://crc12185275-graphql-server.sonraisecurity.com/graphql`

But is rejected by the MCP server.

### 3. Custom Headers
We discovered the MCP server accepts a custom header `sonraisecurity-com-org` (from OPTIONS request), so we tried:

```bash
curl -H "Authorization: Bearer <token>" \
  -H "sonraisecurity-com-org: crc12185275" \
  "https://mcp.s.sonraisecurity.com/stage12902075"
```

**Result:** Same error - `Jwt issuer is not configured`

### 4. OAuth Flow Investigation
We checked for OAuth/OIDC endpoints:
- No redirect to login page when accessing without auth
- No `.well-known/openid-configuration` endpoint (returns 401)
- Server returns JSON errors, not HTML redirects

### 5. Kiro MCP Configuration Attempted

**Current config in `.kiro/settings/mcp.json`:**
```json
{
  "mcpServers": {
    "sonrai": {
      "url": "https://mcp.s.sonraisecurity.com/stage12902075",
      "headers": {
        "Authorization": "Bearer <jwt_token>"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

Kiro supports:
- HTTP/SSE-based MCP servers with custom headers
- OAuth flows (if the server provides proper OAuth endpoints)
- Command-based MCP servers (like `uvx` packages)

## The Problem

The MCP server's JWT validation is configured to reject JWTs with:
- Issuer: "Sonrai"
- Audience: "crc-graphql-server.sonraisecurity.com"

This is the exact JWT format that Sonrai's GraphQL API accepts and expects.

## What Needs to Happen

### Option 1: Fix JWT Validation (Recommended)
Configure the MCP server to accept the same JWTs that work for the GraphQL API:
- Accept issuer: "Sonrai"
- Accept audience: "crc-graphql-server.sonraisecurity.com"
- Use the same JWT validation logic as the GraphQL API

### Option 2: Implement OAuth Flow
If the MCP server requires different authentication, implement a proper OAuth 2.0 flow:
- Provide an authorization endpoint for browser-based login
- Implement token exchange endpoint
- Return MCP-specific tokens after successful authentication
- Document the OAuth configuration for MCP clients

### Option 3: Provide MCP-Specific Token Generation
Create a separate endpoint or UI in Sonrai to generate MCP-specific tokens with the correct issuer/audience that the MCP server expects.

## Testing Endpoints

All tests performed against:
- **MCP Server:** `https://mcp.s.sonraisecurity.com/stage12902075`
- **Org ID:** crc12185275 (stage)
- **User:** cole.horsman@sonraisecurity.com
- **Environment:** Stage (app.s.sonraisecurity.com)

## Questions for Sonrai MCP Team

1. What issuer and audience does the MCP server expect in the JWT?
2. Is there a separate token generation process for MCP access?
3. Does the MCP server support OAuth 2.0? If so, what are the endpoints?
4. Is there MCP-specific documentation for authentication?
5. Why does the MCP server use different JWT validation than the GraphQL API?

## Additional Context

- **IDE:** Kiro (supports MCP via HTTP/SSE with headers or command-based servers)
- **Works in:** VS Code, Claude Desktop, Claude Code (per Matthew)
- **Platform:** macOS
- **Testing Date:** November 24, 2025

We've exhausted all standard authentication approaches. The issue is definitively on the MCP server's JWT validation configuration.

## Update: Kiro Connection Logs

When Kiro attempts to connect, it receives:
```
HTTP 403: Invalid OAuth error response: SyntaxError: Unexpected token '<', "<html>
<h"... is not valid JSON. Raw body: <html>
<head><title>403 Forbidden</title></head>
<body>
<center><h1>403 Forbidden</h1></center>
</body>
</html>
```

**Analysis:**
- Kiro is attempting OAuth negotiation when it sees a `url` field in the MCP config
- The Sonrai MCP server is returning an HTML 403 page instead of a proper OAuth error response
- This suggests the server either:
  1. Doesn't support OAuth at all
  2. Has OAuth endpoints at different paths
  3. Requires specific OAuth parameters that aren't being sent

**Key Question:** How do VS Code and Claude Desktop authenticate to this MCP server? They must be using a different authentication mechanism or configuration format.
