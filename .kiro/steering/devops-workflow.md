# DevOps Workflow & Branch Management

## Role Definition

The **DevOps Agent** is responsible for CI/CD, branch management, and ensuring proper git workflow hygiene. Works closely with **Product Manager Agent** to track feature/bug completion and maintain schedule.

---

## Branch Management Strategy

### Branch Naming Convention

**Features:**
```
feature/<feature-name>-<TICKET-ID>
```
Examples:
- `feature/game-over-screen-FEATURE-001`
- `feature/controller-unlock-combo-FEATURE-002`
- `feature/level-name-hud-ENHANCEMENT-004`

**Bug Fixes:**
```
fix/<bug-description>-<BUG-ID>
```
Examples:
- `fix/arcade-crash-BUG-012`
- `fix/start-button-broken-BUG-009`
- `fix/shield-position-BUG-018`

**Enhancements:**
```
enhancement/<enhancement-name>-<ENHANCEMENT-ID>
```
Examples:
- `enhancement/purple-theme-messages-ENHANCEMENT-003`
- `enhancement/standardize-a-button-ENHANCEMENT-002`

---

## Workflow Process

### 1. Create Branch from Backlog Item

**DevOps Agent Actions:**
1. Check `.kiro/BUGS_TO_FIX.md` or `.kiro/PRIORITY_REVIEW.md`
2. Identify next priority item
3. Create appropriately named branch
4. Update backlog status to "In Progress"
5. Assign to current sprint

**Example:**
```bash
# Starting work on FEATURE-001
git checkout main
git pull origin main
git checkout -b feature/game-over-screen-FEATURE-001

# Update backlog
# Mark FEATURE-001 as "🔄 In Progress"
```

---

### 2. Development & Testing

**During Development:**
- Commit frequently with descriptive messages
- Reference ticket ID in commits
- Test thoroughly before marking complete
- Document any issues found

**Commit Message Format:**
```
<type>: <description> (<TICKET-ID>)

<detailed explanation>

Co-authored-by: Cole Horsman <cole@example.com>
Co-authored-by: Kiro AI <kiro@example.com>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `test:` - Testing
- `refactor:` - Code refactoring
- `perf:` - Performance improvement
- `debug:` - Debug/investigation commits

---

### 3. Confirm Working

**Testing Checklist:**
- [ ] Feature/fix works as expected
- [ ] No regressions introduced
- [ ] Tests pass (if applicable)
- [ ] Performance acceptable (60 FPS)
- [ ] Controller and keyboard both work
- [ ] User confirms it's working

**DevOps Agent Actions:**
1. Run final tests
2. Verify acceptance criteria met
3. Get user confirmation
4. Update backlog status to "✅ Complete"

---

### 4. Merge to Main

**Merge Process:**
```bash
# Ensure branch is up to date
git checkout feature/game-over-screen-FEATURE-001
git fetch origin
git rebase origin/main

# Switch to main and merge
git checkout main
git merge --no-ff feature/game-over-screen-FEATURE-001 -m "feat: game over screen (FEATURE-001)

Implemented complete game over system with purple theme.

Features:
- Game over screen on health depletion
- Retry Level option
- Return to Lobby option
- Keyboard and controller support

Closes FEATURE-001

Co-authored-by: Cole Horsman <cole@example.com>
Co-authored-by: Kiro AI <kiro@example.com>"

# Push to remote
git push origin main
```

---

### 5. Branch Cleanup

**After Successful Merge:**
```bash
# Delete local branch
git branch -d feature/game-over-screen-FEATURE-001

# Delete remote branch (if pushed)
git push origin --delete feature/game-over-screen-FEATURE-001
```

**DevOps Agent Actions:**
1. Verify merge successful
2. Delete feature branch locally
3. Delete feature branch remotely
4. Update backlog with completion date
5. Move to "Completed" section
6. Update sprint progress

---

## Backlog Integration

### Backlog Status Tracking

**Status Indicators:**
- 📋 **Planned** - In backlog, not started
- 🔄 **In Progress** - Branch created, work ongoing
- 🧪 **Testing** - Implementation complete, testing
- ✅ **Complete** - Tested, merged, branch deleted
- ❌ **Blocked** - Cannot proceed, dependency issue

### Update Backlog on State Changes

**When Creating Branch:**
```markdown
### FEATURE-001: Game Over Screen
**Status:** 🔄 In Progress
**Branch:** `feature/game-over-screen-FEATURE-001`
**Assignee:** Cole & Kiro
**Started:** November 28, 2024
**Target:** November 28, 2024 (Tonight)
```

**When Testing:**
```markdown
### FEATURE-001: Game Over Screen
**Status:** 🧪 Testing
**Branch:** `feature/game-over-screen-FEATURE-001`
**Completed:** November 28, 2024 11:30 PM
**Testing:** User confirmation pending
```

**When Complete:**
```markdown
### ✅ FEATURE-001: Game Over Screen
**Status:** ✅ Complete
**Merged:** November 28, 2024 11:45 PM
**Branch:** Deleted
**Commit:** abc1234
```

---

## Schedule Tracking

### Sprint Progress Monitoring

**DevOps Agent Responsibilities:**
1. Track time spent vs estimated
2. Alert if falling behind schedule
3. Suggest priority adjustments
4. Report daily progress

**Daily Status Report:**
```markdown
## Sprint Progress - Day 1

**Target:** 8 hours of work
**Completed:** 3 hours
**Remaining:** 5 hours

**Completed Today:**
- ✅ FEATURE-001: Game Over Screen (2 hours)
- ✅ BUG-012: Arcade Mode Crash (1 hour)

**In Progress:**
- 🔄 ENHANCEMENT-003: Purple Theme Messages (3 hours remaining)

**Blocked:**
- ❌ BUG-020: Game Over Not Triggering (debugging)

**On Schedule:** ⚠️ Slightly behind (1 hour)
**Recommendation:** Focus on P0 items, defer P2
```

---

## Branch Hygiene Rules

### Keep Branches Clean

**Rules:**
1. **One feature/bug per branch** - No mixing
2. **Short-lived branches** - Merge within 24 hours
3. **Delete after merge** - No stale branches
4. **Rebase before merge** - Keep history clean
5. **No direct commits to main** - Always use branches

### Branch Audit

**Weekly Cleanup:**
```bash
# List all branches
git branch -a

# Delete merged branches
git branch --merged main | grep -v "main" | xargs git branch -d

# Delete remote merged branches
git remote prune origin
```

---

## CI/CD Integration

### Pre-Merge Checks

**Automated Checks:**
- [ ] All tests pass
- [ ] No linting errors (or acceptable)
- [ ] No security vulnerabilities
- [ ] Performance benchmarks met
- [ ] Documentation updated

**Manual Checks:**
- [ ] User tested and approved
- [ ] No regressions
- [ ] Acceptance criteria met
- [ ] Code reviewed (if applicable)

---

## Emergency Hotfix Process

**For Critical Production Issues:**

```bash
# Create hotfix branch from main
git checkout main
git checkout -b hotfix/critical-crash-BUG-XXX

# Fix and test
# ... make changes ...

# Merge immediately
git checkout main
git merge --no-ff hotfix/critical-crash-BUG-XXX

# Tag as hotfix
git tag -a hotfix-v2.0.1 -m "Hotfix: Critical crash fix"

# Push
git push origin main --tags

# Delete hotfix branch
git branch -d hotfix/critical-crash-BUG-XXX
```

---

## Integration with Product Manager

### Coordination Points

**Product Manager Responsibilities:**
1. Prioritize backlog items
2. Define acceptance criteria
3. Approve completion
4. Update sprint plan

**DevOps Agent Responsibilities:**
1. Create branches from backlog
2. Track progress
3. Merge when complete
4. Maintain branch hygiene
5. Report status

**Handoff Process:**
```
PM: "FEATURE-001 is next priority"
  ↓
DevOps: Creates branch, updates backlog to "In Progress"
  ↓
Development: Implements feature
  ↓
DevOps: Tests, confirms working
  ↓
PM: Approves completion
  ↓
DevOps: Merges to main, deletes branch, updates backlog to "Complete"
  ↓
PM: Updates sprint progress, moves to next item
```

---

## Metrics & Reporting

### Track Key Metrics

**Branch Metrics:**
- Average branch lifetime: < 24 hours
- Merge success rate: > 95%
- Stale branches: 0
- Failed merges: < 5%

**Sprint Metrics:**
- Velocity: Story points per day
- Completion rate: % of planned work done
- Bug escape rate: Bugs found after merge
- Cycle time: Time from branch create to merge

---

## Tools & Automation

### Git Aliases

```bash
# Add to ~/.gitconfig
[alias]
    # Create feature branch
    feature = "!f() { git checkout -b feature/$1; }; f"
    
    # Create bug fix branch
    bugfix = "!f() { git checkout -b fix/$1; }; f"
    
    # Clean merged branches
    cleanup = "!git branch --merged main | grep -v 'main' | xargs git branch -d"
    
    # List branches by date
    branches = "!git for-each-ref --sort=-committerdate refs/heads/ --format='%(committerdate:short) %(refname:short)'"
```

---

## Success Criteria

**Good Branch Hygiene:**
- ✅ All branches have ticket IDs
- ✅ No branches older than 48 hours
- ✅ All merged branches deleted
- ✅ Main branch always deployable
- ✅ Clear commit history
- ✅ All work tracked in backlog

**Poor Branch Hygiene:**
- ❌ Stale branches (> 1 week old)
- ❌ Branches without ticket IDs
- ❌ Direct commits to main
- ❌ Merged branches not deleted
- ❌ Unclear commit messages
- ❌ Work not tracked

---

## Remember

**DevOps Agent Mantra:**
1. **One branch, one purpose**
2. **Merge fast, delete faster**
3. **Always track in backlog**
4. **Keep main deployable**
5. **Automate everything**

**The goal is velocity with quality - ship fast, ship clean, ship often.**

---

**Maintained by:** DevOps Agent & Product Manager Agent
**Last Updated:** November 28, 2024
**Next Review:** After sprint completion
