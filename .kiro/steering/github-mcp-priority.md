# GitHub MCP Priority Usage

## CRITICAL: Always Use GitHub MCP First

When dealing with ANY of the following, you MUST use GitHub MCP tools before any other approach:

## CI/CD & Automation

### GitHub Actions Workflows
- **Check workflow status**: Use `list_commits` or check PR status
- **View workflow runs**: Check recent runs and their status
- **Debug failures**: Get logs and error messages
- **Monitor deployments**: Track deployment status

### Pipeline Failures
- **Investigate failures**: Get detailed error logs
- **Check test results**: Review test job outputs
- **Verify fixes**: Confirm new runs pass after changes

## Security & Compliance

### Security Scanning
- **Dependabot alerts**: Check for dependency vulnerabilities
- **Code scanning**: Review static analysis findings
- **Secret scanning**: Check for exposed secrets
- **Security advisories**: Monitor security updates

### Code Quality
- **Branch protection**: Verify protection rules
- **Required reviews**: Check review requirements
- **Status checks**: Ensure required checks pass

## Repository Operations

### Pull Requests
- **List PRs**: Filter by status, author, labels
- **Review PRs**: Get files changed, comments, reviews
- **Check CI status**: Verify all checks pass
- **Merge PRs**: Merge after approval
- **Update branches**: Keep PR branches current

### Issues
- **Create issues**: From backlog, bugs, features
- **Update issues**: Change status, labels, assignees
- **Comment on issues**: Add updates, test results
- **Search issues**: Find related issues
- **Link issues**: Connect issues to PRs

### Branches
- **Create branches**: For features, fixes, experiments
- **List branches**: See all active branches
- **Check branch status**: Verify branch is up to date

### Commits
- **View history**: See recent commits
- **Check changes**: Review what changed
- **Find commits**: Search by message, author, file

## Code Discovery

### Search Operations
- **Search code**: Find implementations across repos
- **Search issues**: Find related problems/solutions
- **Search repositories**: Discover similar projects
- **Get file contents**: Read files from any repo

## Release Management

### Releases & Tags
- **Create releases**: Tag versions
- **Update changelogs**: Document changes
- **Track versions**: Monitor release history

## Workflow Examples

### Example 1: Investigating Test Failure
```
User: "Tests are failing in CI"

Agent Response:
1. Use GitHub MCP: "List recent workflow runs for this repo"
2. Use GitHub MCP: "Get details of the failed workflow run"
3. Use GitHub MCP: "Show me the logs for the pytest job"
4. Analyze error messages
5. Fix issues in code
6. Use GitHub MCP: "Check if latest run passed"
```

### Example 2: Creating Feature from Backlog
```
User: "Implement the raygun visual improvement"

Agent Response:
1. Use GitHub MCP: "Create issue 'Improve Raygun Visual' with label 'enhancement'"
2. Use GitHub MCP: "Create branch feature/improved-raygun from main"
3. Implement changes in code
4. Run tests locally
5. Use GitHub MCP: "Create PR from feature/improved-raygun to main"
6. Use GitHub MCP: "Check PR status and CI results"
```

### Example 3: Security Audit
```
User: "Check for security issues"

Agent Response:
1. Use GitHub MCP: "List Dependabot alerts for this repo"
2. Use GitHub MCP: "Show code scanning alerts"
3. Use GitHub MCP: "Check branch protection rules"
4. Review findings and prioritize
5. Use GitHub MCP: "Create issues for critical vulnerabilities"
```

### Example 4: PR Review Process
```
User: "Review PR #42"

Agent Response:
1. Use GitHub MCP: "Get details of PR #42"
2. Use GitHub MCP: "Show files changed in PR #42"
3. Use GitHub MCP: "Get PR status checks for PR #42"
4. Use GitHub MCP: "Show review comments on PR #42"
5. Review code changes
6. Use GitHub MCP: "Add review comment on PR #42"
7. If approved: Use GitHub MCP: "Merge PR #42"
```

### Example 5: Monitoring Deployments
```
User: "Did the deployment succeed?"

Agent Response:
1. Use GitHub MCP: "List recent workflow runs"
2. Use GitHub MCP: "Get status of deployment workflow"
3. If failed: Use GitHub MCP: "Get logs for deployment job"
4. Report status and any errors
```

## Available GitHub MCP Tools

### Read Operations (Auto-approved)
- `list_issues` - List and filter issues
- `get_issue` - Get issue details
- `list_pull_requests` - List and filter PRs
- `get_pull_request` - Get PR details
- `get_pull_request_files` - See PR changes
- `get_pull_request_status` - Check CI/CD status
- `get_pull_request_comments` - Read comments
- `get_pull_request_reviews` - Read reviews
- `list_commits` - View commit history
- `search_repositories` - Search repos
- `search_code` - Search code
- `search_issues` - Search issues/PRs
- `get_file_contents` - Read files

### Write Operations (Require approval)
- `create_issue` - Create issue
- `update_issue` - Modify issue
- `add_issue_comment` - Comment on issue
- `create_pull_request` - Create PR
- `create_pull_request_review` - Review PR
- `merge_pull_request` - Merge PR
- `update_pull_request_branch` - Update PR
- `create_branch` - Create branch
- `push_files` - Push changes
- `create_or_update_file` - Modify file
- `create_repository` - Create repo
- `fork_repository` - Fork repo

## When NOT to Use GitHub MCP

- **Local file operations**: Use Kiro's file tools
- **Running tests locally**: Use pytest directly
- **Game development**: Use existing Python tools
- **API integration**: Use `src/sonrai_client.py`
- **Documentation writing**: Use file tools

## Priority Rule

**If it involves GitHub (repos, issues, PRs, CI/CD, security), use GitHub MCP FIRST.**

This ensures:
- Real-time data from GitHub
- Proper authentication and permissions
- Accurate status information
- Efficient API usage
- Consistent workflow
