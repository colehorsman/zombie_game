# Architecture Review Board & Backlog Synchronization

## Overview

The Architecture Review Board (ARB) Report and BACKLOG.md are **living documents** that must stay synchronized. This document explains the automated synchronization system and manual maintenance procedures.

---

## Automated Synchronization

### Hook 1: `sync-arb-with-backlog.kiro.hook`

**Trigger:** When BACKLOG.md is edited
**Owner:** Architecture Agent
**Purpose:** Update ARB report to reflect completed work

**Actions:**
1. Identify completed ARB recommendations in backlog
2. Update relevant agent assessments (+0.5 to +1.0 points)
3. Recalculate overall weighted average score
4. Update sprint plan progress
5. Document changes in "Recent Updates" section
6. Commit changes with descriptive message

**Example Flow:**
```
User marks DEVEX-001 as complete in BACKLOG.md
    ↓
Hook triggers Architecture Agent
    ↓
Agent reads both documents
    ↓
Agent updates DevEx score: 6.0 → 6.5
    ↓
Agent recalculates overall: 7.4 → 7.45
    ↓
Agent commits ARB report update
```

### Hook 2: `arb-report-updated.kiro.hook`

**Trigger:** When ARCHITECTURE_REVIEW_BOARD_REPORT.md is edited
**Owner:** Product Manager Agent
**Purpose:** Sync new recommendations to backlog

**Actions:**
1. Identify new recommendations in ARB report
2. Add missing items to BACKLOG.md
3. Update priority sections (P0/P1/P2)
4. Mark completed items
5. Update backlog status header
6. Commit changes with descriptive message

**Example Flow:**
```
Architecture Agent adds new recommendation ARCH-005
    ↓
Hook triggers Product Manager
    ↓
PM reads both documents
    ↓
PM adds ARCH-005 to P1 section in backlog
    ↓
PM updates backlog status
    ↓
PM commits backlog update
```

---

## Score Calculation System

### Overall Score Formula

```
Overall Score = (Sum of all 12 agent scores) / 12
```

### Agent Score Updates

When recommendations are completed, update agent scores:

**Minor Improvement (+0.5 points):**
- Single P2 recommendation completed
- Documentation updates
- Small bug fixes

**Moderate Improvement (+0.75 points):**
- Single P1 recommendation completed
- Multiple P2 recommendations completed
- Significant feature additions

**Major Improvement (+1.0 points):**
- P0 recommendation completed
- Multiple P1 recommendations completed
- Fundamental architecture improvements

**Example:**
```
DevEx Agent starts at 6.0/10
Complete DEVEX-001 (P0: Create CONTRIBUTING.md) → +1.0
Complete DEVEX-002 (P0: Create TROUBLESHOOTING.md) → +1.0
New DevEx score: 8.0/10

Overall score impact:
Old: (88.5) / 12 = 7.375
New: (90.5) / 12 = 7.542
Rounded: 7.4 → 7.5
```

### Score Boundaries

- **9.0-10.0:** Excellent - Production-ready, best practices
- **8.0-8.9:** Very Good - Strong foundation, minor improvements
- **7.0-7.9:** Good - Solid work, needs attention in areas
- **6.0-6.9:** Acceptable - Functional, significant improvements needed
- **5.0-5.9:** Needs Work - Critical gaps, requires focus
- **< 5.0:** Critical - Blocking issues, immediate action required

---

## Document Structure

### ARB Report Structure

```markdown
# Architecture Review Board Report

## Recent Updates
[Latest changes, score updates, completed work]

## Review Board Composition
[12 agents with their domains]

## Overall Assessment
[Weighted average score with breakdown]

## Agent Reviews & Recommendations
[Individual agent sections with scores and recommendations]

## Summary of Recommendations
[Organized by priority]

## Recommended Sprint Plan
[Sprint breakdown with stories]

## Conclusion
[Overall assessment and strategic recommendations]
```

### Backlog Structure

```markdown
# BACKLOG.md

## Current Status
[Overall health, P0/P1/P2 counts, current sprint]

## P0 - Critical
[Urgent items with hard deadlines]

## P1 - High Priority
[Important items for current/next sprint]

## P2 - Medium Priority
[Nice-to-have improvements]

## Completed
[Finished items with completion dates]
```

---

## Manual Maintenance Procedures

### When Completing a Task

1. **Mark in BACKLOG.md:**
   ```markdown
   - [x] [ARCH-001] Continue game_engine.py refactoring (L: 2-3 days)
   ```

2. **Hook automatically:**
   - Architecture Agent updates ARB report
   - Recalculates scores
   - Commits changes

3. **Verify sync:**
   - Check ARB report shows update
   - Verify score changed appropriately
   - Confirm commit message is clear

### When Adding New Recommendations

1. **Add to ARB Report:**
   ```markdown
   ### X. Agent Name Review

   **Recommendations:**

   **P1 - High Priority:**
   1. **[AGENT-###] New recommendation** (M: 4-6 hours)
      - Description
      - Benefit
   ```

2. **Hook automatically:**
   - Product Manager adds to BACKLOG.md
   - Places in correct priority section
   - Updates status header

3. **Verify sync:**
   - Check backlog has new item
   - Verify priority placement
   - Confirm sprint assignment if applicable

### When Changing Priorities

1. **Update in ARB Report:**
   - Move recommendation between P0/P1/P2 sections
   - Update sprint plan if needed

2. **Hook automatically:**
   - Product Manager moves in backlog
   - Adjusts sprint assignments
   - Updates velocity estimates

3. **Verify sync:**
   - Check backlog reflects new priority
   - Verify sprint plan updated

---

## Best Practices

### For Architecture Agent

**When updating ARB report:**
- ✅ Always recalculate overall score
- ✅ Document reason for score changes
- ✅ Update "Recent Updates" section
- ✅ Be conservative with score increases (evidence-based)
- ✅ Commit with clear message

**Don't:**
- ❌ Arbitrarily change scores without completed work
- ❌ Skip recalculation of overall score
- ❌ Forget to update sprint plan
- ❌ Make changes without documentation

### For Product Manager

**When updating backlog:**
- ✅ Keep priority sections organized
- ✅ Update status header regularly
- ✅ Reference ARB recommendations
- ✅ Track sprint velocity
- ✅ Mark completed items promptly

**Don't:**
- ❌ Add items without ARB reference
- ❌ Skip priority classification
- ❌ Forget to update sprint assignments
- ❌ Leave completed items in active sections

---

## Troubleshooting

### Hooks Not Triggering

**Problem:** File edited but hook didn't run

**Solutions:**
1. Check hook is enabled: `"enabled": true`
2. Verify file pattern matches: `.kiro/BACKLOG.md`
3. Check Kiro hook settings in IDE
4. Manually trigger: Open hook UI and run manually

### Scores Out of Sync

**Problem:** Overall score doesn't match agent scores

**Solutions:**
1. Manually recalculate: Sum all 12 scores ÷ 12
2. Check for rounding errors
3. Verify all agent scores are current
4. Update ARB report with correct calculation

### Missing Recommendations

**Problem:** ARB recommendation not in backlog

**Solutions:**
1. Manually add to backlog with correct format
2. Reference ARB recommendation ID
3. Place in correct priority section
4. Update backlog status header

### Duplicate Items

**Problem:** Same recommendation in both documents

**Solutions:**
1. Check ARB recommendation ID matches backlog
2. Consolidate to single entry
3. Ensure hook ran correctly
4. Update both documents if needed

---

## Metrics & Reporting

### Weekly Review

Every Friday, review synchronization:
- [ ] All completed backlog items reflected in ARB
- [ ] All ARB recommendations in backlog
- [ ] Overall score is accurate
- [ ] Sprint plan is current
- [ ] No orphaned items

### Monthly Audit

Every month, full audit:
- [ ] Recalculate all agent scores from scratch
- [ ] Verify all 47 recommendations accounted for
- [ ] Check for drift between documents
- [ ] Update sprint velocity
- [ ] Adjust priorities based on progress

---

## Integration with Other Agents

### With Kiroween Submission Agent

**Priority Override:**
- Kiroween tasks (KIRO-001 through KIRO-004) take absolute priority
- Hard deadline: Dec 5, 2025
- All other work can be deprioritized for submission

**Score Impact:**
- Completing Kiroween tasks increases Kiroween agent score
- Successful submission could boost overall score to 7.5+
- Document submission preparation in ARB report

### With QA Agent

**Test Coverage Impact:**
- Completing QA recommendations improves QA score
- Test coverage increases boost overall quality
- Document test improvements in ARB report

### With Security Agent

**Security Posture Impact:**
- Completing security recommendations improves Security score
- Vulnerability fixes boost overall security
- Document security improvements in ARB report

---

## Success Criteria

**Synchronization is successful when:**
- ✅ Both documents updated within 5 minutes of each other
- ✅ Overall score accurately reflects agent scores
- ✅ All ARB recommendations have backlog entries
- ✅ All backlog items reference ARB recommendations
- ✅ Sprint plan matches backlog priorities
- ✅ Completed items marked in both documents
- ✅ Commit messages clearly describe changes

---

## Future Enhancements

### Potential Improvements

1. **Automated Testing:**
   - Script to verify synchronization
   - Check score calculations
   - Validate document structure

2. **Dashboard:**
   - Visual representation of scores
   - Progress tracking
   - Burndown charts

3. **Notifications:**
   - Alert when sync fails
   - Notify on score changes
   - Remind of weekly review

4. **Analytics:**
   - Track score trends over time
   - Measure velocity
   - Predict completion dates

---

## Remember

**The ARB Report and BACKLOG.md are living documents that reflect the current state of the project. Keep them synchronized, accurate, and up-to-date through automated hooks and manual maintenance.**

**Key Principle:** Every completed task should improve at least one agent's score, which improves the overall project health score. This creates a measurable feedback loop that demonstrates continuous improvement.

---

**Maintained by:** Architecture Agent & Product Manager Agent
**Last Updated:** November 28, 2024
**Next Review:** After Kiroween submission (Dec 5, 2025)
