# Documentation Standards

This document defines the documentation standards for Sonrai Zombie Blaster, following AWS and Kiro best practices.

## Standards Overview

### AWS Documentation Standards

We follow AWS documentation principles:

1. **Action-Oriented** - Start with verbs
   - ✅ "Configure the API client"
   - ❌ "API client configuration"

2. **Task-Focused** - Organize by user goals
   - ✅ "How to add a new quest"
   - ❌ "Quest system implementation details"

3. **Progressive Disclosure** - Use expandable sections
   ```markdown
   <details>
   <summary><b>Advanced Configuration</b></summary>
   
   Detailed content here...
   
   </details>
   ```

4. **Scannable** - Easy to skim
   - Use bullet points
   - Clear headings
   - Tables for comparisons
   - Code blocks for examples

5. **Consistent** - Same structure across docs
   - All guides follow same template
   - All reference docs use same format

### Kiro Documentation Standards

We follow Kiro documentation principles:

1. **Evidence-Based** - Back every claim
   ```markdown
   ❌ "The game is fast"
   ✅ "The game maintains 60 FPS with 500+ entities through spatial 
       grid optimization (18.5× speedup)"
   ```

2. **Show, Don't Tell** - Code examples
   ```markdown
   ### Spatial Grid Optimization
   
   **Problem:** O(n²) collision detection
   
   \`\`\`python
   # Before: Check every projectile against every zombie
   for projectile in projectiles:
       for zombie in zombies:
           check_collision(projectile, zombie)
   \`\`\`
   
   **Solution:** Spatial partitioning
   
   \`\`\`python
   # After: Only check nearby cells
   nearby = grid.get_nearby_zombies(projectile)
   for zombie in nearby:
       check_collision(projectile, zombie)
   \`\`\`
   
   **Impact:** 18.5× speedup, 15 FPS → 60 FPS
   ```

3. **Multiple Audiences** - Write for different readers
   - Developers: Technical details, code examples
   - Decision Makers: Business value, ROI
   - Users: How-to guides, troubleshooting

4. **Comprehensive Testing** - Document test coverage
   - Test statistics
   - Coverage percentages
   - Example tests

5. **Real-World Focus** - Use cases and impact
   - How it's used in practice
   - Measurable outcomes
   - Success stories

## Documentation Structure

### Root Directory (Minimal)

Keep root clean with only essential files:

```
/
├── README.md              # Project overview with expandable sections
├── QUICKSTART.md          # Optional: 60-second setup
├── BACKLOG.md             # Feature roadmap
├── LICENSE                # License file
├── .env.example           # Configuration template
└── docs/                  # All documentation
```

### Documentation Hub (docs/)

Organize by purpose and audience:

```
docs/
├── README.md                    # Central hub with navigation
│
├── guides/                      # How-to guides (task-focused)
│   ├── QUICKSTART.md           # Get started
│   ├── INSTALLATION.md         # Detailed setup
│   ├── CONFIGURATION.md        # Environment config
│   ├── DEVELOPMENT_SETUP.md    # Dev environment
│   ├── TESTING.md              # Running tests
│   ├── DEBUGGING.md            # Debug tools
│   ├── QUESTS.md               # Quest system
│   ├── ARCADE_MODE.md          # Arcade mode
│   └── POWERUPS.md             # Power-ups
│
├── architecture/                # Technical deep dives
│   ├── ARCHITECTURE.md         # System design
│   ├── PERFORMANCE.md          # Optimization
│   ├── PATTERNS.md             # Design patterns
│   ├── PROJECT_SHOWCASE.md     # Achievements
│   └── INNOVATION.md           # Unique features
│
├── reference/                   # API and reference
│   ├── API.md                  # API reference
│   ├── MECHANICS.md            # Game mechanics
│   ├── CONTROLS.md             # Input reference
│   ├── CHANGELOG.md            # Version history
│   ├── TROUBLESHOOTING.md      # Common issues
│   ├── PROJECT_SUMMARY.md      # Executive summary
│   └── REPOSITORY_STRUCTURE.md # Codebase org
│
├── community/                   # Contributing
│   ├── CONTRIBUTING.md         # How to contribute
│   ├── DEVELOPMENT.md          # Workflow
│   └── STANDARDS.md            # Code standards
│
└── sonrai-api/                  # API-specific
    ├── README.md               # API overview
    ├── INTEGRATION_GUIDE.md    # Integration
    ├── QUICK_REFERENCE.md      # Quick ref
    └── queries/                # Query examples
```

## Writing Guidelines

### Document Templates

#### Guide Template

```markdown
# [Action] Guide

Brief description of what this guide helps you accomplish.

## Prerequisites

- Requirement 1
- Requirement 2

## Steps

### 1. First Step

Description and code example.

### 2. Second Step

Description and code example.

## Verification

How to verify it worked.

## Troubleshooting

Common issues and solutions.

## Next Steps

- Related guide 1
- Related guide 2
```

#### Reference Template

```markdown
# [Topic] Reference

Complete reference for [topic].

## Overview

Brief description.

## [Section 1]

### [Item 1]

**Description:** What it does

**Parameters:**
- `param1` - Description
- `param2` - Description

**Returns:** What it returns

**Example:**
\`\`\`python
example_code()
\`\`\`

## See Also

- Related reference 1
- Related reference 2
```

### Progressive Disclosure

Use expandable sections for depth:

```markdown
## Features

<details>
<summary><b>🚀 Getting Started</b></summary>

Content that expands...

</details>

<details>
<summary><b>🏗️ Architecture</b></summary>

Content that expands...

</details>
```

**Benefits:**
- Scannable at a glance
- Expand only what you need
- Clean visual hierarchy
- Mobile-friendly

### Code Examples

Every code example must include:

1. **Context** - What problem does this solve?
2. **Code** - Working, tested example
3. **Explanation** - How does it work?
4. **Impact** - What's the result?

**Example:**

```markdown
### Problem: Collision Detection Performance

With 500 zombies, naive collision detection was O(n²):

\`\`\`python
# Naive approach - 5,000 checks per frame
for projectile in projectiles:
    for zombie in zombies:
        if projectile.collides_with(zombie):
            handle_collision()
\`\`\`

**Solution:** Spatial grid partitioning:

\`\`\`python
class SpatialGrid:
    def get_nearby_zombies(self, projectile):
        # Only check 9 cells instead of all zombies
        cell_x = int(projectile.x // cell_size)
        cell_y = int(projectile.y // cell_size)
        
        nearby = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nearby.extend(grid[cell_x + dx][cell_y + dy])
        return nearby
\`\`\`

**Impact:** 18.5× speedup, 15 FPS → 60 FPS
```

### Mathematical Notation

Use LaTeX for formulas:

```markdown
Time complexity without optimization:
$$T_{naive} = n \times m \times t_{check}$$

Time complexity with spatial grid:
$$T_{grid} = m \times t_{insert} + n \times k \times t_{check}$$

Where $k$ = average entities per cell (typically 3)
```

### Diagrams

Use ASCII art for simple diagrams:

```
┌─────────────┐
│  Component  │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  Component  │
└─────────────┘
```

### Tables

Use tables for comparisons:

| Before | After | Improvement |
|--------|-------|-------------|
| 15 FPS | 60 FPS | 4× faster |
| O(n²) | O(n) | Linear scaling |

## Quality Checklist

Before publishing documentation:

- [ ] Follows AWS standards (action-oriented, task-focused)
- [ ] Follows Kiro standards (evidence-based, code examples)
- [ ] Uses progressive disclosure (expandable sections)
- [ ] Includes working code examples
- [ ] Provides metrics and benchmarks
- [ ] Has clear navigation
- [ ] Links to related docs
- [ ] Tested for accuracy
- [ ] Reviewed for clarity
- [ ] Spell-checked

## Maintenance

### When to Update

Update documentation when:
- Adding new features
- Fixing bugs
- Changing APIs
- Improving performance
- Refactoring code

### Review Process

Documentation should be reviewed for:

**Accuracy:**
- Code examples work
- Metrics are current
- Links are valid

**Clarity:**
- Concepts explained simply
- Examples are clear
- No jargon without explanation

**Completeness:**
- All features documented
- Edge cases covered
- Troubleshooting included

## Success Metrics

Good documentation should:

1. **Reduce support questions** - Users find answers themselves
2. **Accelerate onboarding** - New contributors productive quickly
3. **Increase adoption** - Clear value proposition attracts users
4. **Enable contributions** - Community can extend the project
5. **Showcase excellence** - Technical sophistication is evident

---

**These standards ensure our documentation is world-class and competition-ready.**
