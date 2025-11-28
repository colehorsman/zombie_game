# MCP Tools Usage Guide

## Available MCP Servers

This project uses Model Context Protocol (MCP) servers to extend Kiro's capabilities for development workflows.

## Configured Servers

### 1. GitHub (`@modelcontextprotocol/server-github`)

**Purpose:** Manage GitHub repository operations directly from Kiro

**Use Cases:**
- **Backlog Management** - Create issues from BACKLOG.md items
- **Bug Tracking** - File bug reports with reproduction steps
- **Feature Branches** - Check PR status, review code
- **Release Management** - Tag releases, update changelogs
- **Documentation** - Search code examples across repos

**Common Operations:**
```
# Search for similar implementations
"Search GitHub for pygame collision detection examples"

# Create issue from backlog item
"Create GitHub issue for JIT Access Quest feature"

# Check PR status
"List open PRs for this repository"

# Get file from another repo
"Get the README from modelcontextprotocol/servers"
```

**Setup:**
1. Generate GitHub Personal Access Token at https://github.com/settings/tokens
2. Required scopes: `repo`, `read:org`
3. Add token to `.kiro/settings/mcp.json` under `GITHUB_PERSONAL_ACCESS_TOKEN`

**Auto-approved tools:**
- `list_issues` - Safe read operation
- `search_repositories` - Safe search operation
- `get_file_contents` - Safe read operation

**Requires approval:**
- `create_issue` - Creates new issue
- `create_pull_request` - Creates new PR
- `push_files` - Modifies repository

### 2. Brave Search (`@modelcontextprotocol/server-brave-search`)

**Purpose:** Research cloud security concepts, validate educational content, find documentation

**Use Cases:**
- **Educational Content** - Verify security breach examples are accurate
- **Technical Research** - Find AWS IAM best practices, Pygame optimization techniques
- **Documentation** - Look up API documentation, library usage examples
- **Fact Checking** - Validate claims in educational materials
- **Competitive Analysis** - Research similar security games/tools

**Common Operations:**
```
# Research security concepts
"Search for recent AWS IAM security breaches to include in game"

# Technical documentation
"Search for pygame spatial grid optimization techniques"

# Validate educational content
"Search for statistics on unused cloud identities"

# Find examples
"Search for examples of JIT access implementation in AWS"
```

**Setup:**
1. Get Brave Search API key at https://brave.com/search/api/
2. Free tier: 2,000 queries/month
3. Add key to `.kiro/settings/mcp.json` under `BRAVE_API_KEY`

**Auto-approved tools:**
- `brave_web_search` - Safe read-only search operation

### 3. Sonrai (`sonrai` custom server)

**Purpose:** Direct integration with Sonrai Security API (currently disabled)

**Status:** Disabled - using direct API integration via `src/sonrai_client.py` instead

**Note:** This MCP server is available but not actively used. The game uses direct GraphQL API calls for better control and error handling.

## When to Use MCP Tools

### Use GitHub MCP When:
- Creating issues from backlog items
- Checking PR status before merging
- Searching for code examples in other repos
- Managing releases and tags
- Reviewing code changes

### Use Brave Search When:
- Validating educational content accuracy
- Researching new security concepts to add
- Finding technical documentation
- Looking for real-world breach examples
- Checking AWS best practices

### Don't Use MCP When:
- Direct file operations (use Kiro's file tools)
- Running tests (use pytest directly)
- Game development (use existing tools)
- API integration (use `src/sonrai_client.py`)

## Best Practices

### 1. Research Before Implementation
Before adding new security concepts to the game:
```
1. Use Brave Search to research the concept
2. Validate with AWS documentation
3. Check Sonrai's approach
4. Implement with accurate information
```

### 2. Issue Management Workflow
When working on backlog items:
```
1. Review BACKLOG.md
2. Create GitHub issue with details
3. Create feature branch
4. Implement and test
5. Create PR via GitHub MCP
6. Update BACKLOG.md
```

### 3. Documentation Validation
When updating educational content:
```
1. Draft content
2. Use Brave Search to fact-check claims
3. Verify statistics and examples
4. Add sources to documentation
5. Update docs with validated content
```

### 4. Competitive Research
When considering new features:
```
1. Search for similar implementations
2. Analyze what works well
3. Identify gaps we can fill
4. Design our unique approach
5. Document decisions
```

## Configuration Management

### Workspace Config (`.kiro/settings/mcp.json`)
- Project-specific MCP servers
- Shared across team members
- Committed to git (without secrets)

### User Config (`~/.kiro/settings/mcp.json`)
- Personal API keys and tokens
- Not committed to git
- User-specific settings

### Adding API Keys

**Never commit API keys to git!** Add them to your user config:

```bash
# Edit user config (outside workspace)
nano ~/.kiro/settings/mcp.json
```

Add your keys:
```json
{
  "mcpServers": {
    "github": {
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_your_actual_token_here"
      }
    },
    "brave-search": {
      "env": {
        "BRAVE_API_KEY": "your_actual_key_here"
      }
    }
  }
}
```

## Troubleshooting

### GitHub MCP Not Working
1. Check token has correct scopes (`repo`, `read:org`)
2. Verify token is in user config, not workspace config
3. Check server status in MCP Server view
4. Try reconnecting server

### Brave Search Not Working
1. Verify API key is valid
2. Check monthly quota (2,000 queries/month on free tier)
3. Ensure key is in user config
4. Test with simple search query

### Server Won't Start
1. Ensure `npx` is installed (`npm install -g npx`)
2. Check internet connection (downloads packages on first run)
3. View server logs in MCP Server view
4. Try disabling and re-enabling server

## Security Notes

- **API Keys** - Store in user config only, never commit
- **Auto-approve** - Only safe read operations are auto-approved
- **Tokens** - Rotate GitHub tokens periodically
- **Quotas** - Monitor Brave Search usage to avoid hitting limits

## Future MCP Servers

Potential additions as project grows:
- **Postgres/SQLite** - Player analytics and telemetry
- **Slack** - Team collaboration and demo coordination
- **Memory** - Maintain context about design decisions
- **Filesystem** - Advanced asset management (if needed)

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [GitHub MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/github)
- [Brave Search API](https://brave.com/search/api/)
- [Kiro MCP Guide](https://docs.kiro.ai/mcp)
