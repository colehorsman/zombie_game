# MCP Tools Usage Guide

## Available MCP Servers

This project uses Model Context Protocol (MCP) servers to extend Kiro's capabilities for development workflows.

## Configured Servers

### Known Issue: npx-based MCP Servers

**Status:** There is currently a compatibility issue between Kiro's MCP client and npx-based MCP servers (Brave Search, Fetch). These servers fail to maintain connections with error "MCP error -32000: Connection closed". This is a known limitation being investigated.

**Workaround:** Use GitHub MCP for repository operations and direct curl/requests for web research until this is resolved.

### 1. GitHub (`@modelcontextprotocol/server-github`)

**Purpose:** Manage GitHub repository operations directly from Kiro

**Status:** ✅ Working

**Use Cases:**
- **Backlog Management** - Create issues from BACKLOG.md items
- **Bug Tracking** - File bug reports with reproduction steps
- **Feature Branches** - Check PR status, review code
- **Release Management** - Tag releases, update changelogs
- **Documentation** - Search code examples across repos

**Common Operations:**
```
# CI/CD & Pipeline
"Check the status of the latest GitHub Actions workflow"
"Show me failed workflow runs from the last week"
"Get the logs for the failed pytest job"
"List all workflow runs for the main branch"

# Security & Code Quality
"Show me any Dependabot alerts for this repo"
"Check for security vulnerabilities in dependencies"
"List code scanning alerts"
"Review branch protection rules"

# Pull Requests
"List open PRs for this repository"
"Show me the files changed in PR #42"
"Get the review comments on the latest PR"
"Check if PR #42 has passing status checks"
"Merge PR #42 after approval"

# Issues & Backlog
"Create GitHub issue for JIT Access Quest feature"
"List open issues labeled 'bug'"
"Show issues assigned to me"
"Add comment to issue #15 with test results"

# Code Search & Review
"Search GitHub for pygame collision detection examples"
"Get the README from modelcontextprotocol/servers"
"Show me recent commits to src/game_engine.py"
"Find all files that import pygame in this repo"

# Branches & Releases
"Create a new branch called feature/arcade-mode"
"List all branches in this repository"
"Create a release tag v2.0.0"
"Get the latest release notes"
```

**Setup:**
1. Generate GitHub Personal Access Token at https://github.com/settings/tokens
2. Required scopes: `repo`, `read:org`
3. Add token to `.kiro/settings/mcp.json` under `GITHUB_PERSONAL_ACCESS_TOKEN`

**Auto-approved tools (read-only):**
- `list_issues` - List and filter issues
- `get_issue` - Get issue details
- `search_repositories` - Search for repos
- `search_code` - Search code across repos
- `search_issues` - Search issues and PRs
- `get_file_contents` - Read file contents
- `list_commits` - View commit history
- `get_pull_request` - Get PR details
- `list_pull_requests` - List and filter PRs
- `get_pull_request_files` - See PR file changes
- `get_pull_request_status` - Check CI/CD status
- `get_pull_request_comments` - Read PR comments
- `get_pull_request_reviews` - Read PR reviews

**Requires approval (write operations):**
- `create_issue` - Create new issue
- `update_issue` - Modify issue
- `add_issue_comment` - Comment on issue
- `create_pull_request` - Create new PR
- `create_pull_request_review` - Review PR
- `merge_pull_request` - Merge PR
- `update_pull_request_branch` - Update PR branch
- `create_branch` - Create new branch
- `push_files` - Push file changes
- `create_or_update_file` - Modify files
- `create_repository` - Create new repo
- `fork_repository` - Fork a repo

### 2. Brave Search (`@modelcontextprotocol/server-brave-search`)

**Purpose:** Research cloud security concepts, validate educational content, find documentation

**Status:** ⚠️ Disabled - Connection issues with Kiro MCP client

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

### 3. Fetch (`@modelcontextprotocol/server-fetch`)

**Purpose:** Retrieve web pages and documentation without API keys

**Status:** ⚠️ Disabled - Connection issues with Kiro MCP client

### 4. Sonrai (`sonrai` custom server)

**Purpose:** Direct integration with Sonrai Security API

**Status:** ✅ Available but disabled - using direct API integration via `src/sonrai_client.py` instead

**Note:** This MCP server is available but not actively used. The game uses direct GraphQL API calls for better control and error handling.

## When to Use MCP Tools

### ALWAYS Use GitHub MCP For:

**CI/CD & Pipeline Operations:**
- Check GitHub Actions workflow status
- Investigate pipeline failures
- Review workflow run logs
- List failed jobs and their errors
- Check deployment status
- Monitor build history

**Security & Code Quality:**
- Review security scan results
- Check Dependabot alerts
- Investigate code scanning findings
- Review secret scanning alerts
- Check branch protection rules
- Audit security policies

**Repository Management:**
- Create issues from backlog items
- Check PR status and reviews
- List open/closed PRs with filters
- Get PR file changes and diffs
- Review PR comments and feedback
- Merge PRs after approval
- Create and manage branches

**Code Review & Collaboration:**
- Search code across repositories
- Get file contents from any repo
- Review commit history
- Check who changed what and when
- Find similar implementations
- Review code review comments

**Release Management:**
- Create releases and tags
- Update changelogs
- Track release notes
- Monitor version history

**Issue Tracking:**
- Create issues with labels/assignees
- Update issue status
- Add comments to issues
- Search issues by criteria
- Link issues to PRs
- Track bug reports

### Use Brave Search When:
⚠️ Currently disabled due to connection issues
- Validating educational content accuracy
- Researching new security concepts to add
- Finding technical documentation
- Looking for real-world breach examples
- Checking AWS best practices

### Don't Use MCP When:
- Direct file operations (use Kiro's file tools)
- Running tests locally (use pytest directly)
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
2. Use GitHub MCP: "Create issue for [feature] with label 'enhancement'"
3. Use GitHub MCP: "Create branch feature/[name] from main"
4. Implement and test locally
5. Use GitHub MCP: "Create PR from feature/[name] to main"
6. Use GitHub MCP: "Check PR status and CI results"
7. Use GitHub MCP: "Merge PR after approval"
8. Update BACKLOG.md
```

### 2.5. CI/CD Monitoring Workflow
When checking build/test status:
```
1. Use GitHub MCP: "Show latest workflow runs"
2. If failures: "Get logs for failed [job-name] job"
3. Analyze error messages
4. Fix issues locally
5. Push changes
6. Use GitHub MCP: "Check if new workflow run passed"
```

### 2.6. Security Monitoring Workflow
Regular security checks:
```
1. Use GitHub MCP: "List Dependabot alerts"
2. Use GitHub MCP: "Show code scanning alerts"
3. Review and prioritize findings
4. Create issues for critical vulnerabilities
5. Fix and verify with GitHub MCP
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
