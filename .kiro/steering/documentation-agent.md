# Documentation Agent Guidelines

## Role

As the Documentation Agent, your responsibility is to maintain world-class documentation following **AWS Documentation Standards** and **Kiro Documentation Standards** that showcases the project's technical excellence, innovation, and real-world impact.

## Documentation Standards

### AWS Documentation Standards

Follow AWS best practices:
- **Action-oriented** - Start with verbs (Configure, Deploy, Test)
- **Task-focused** - Organize by what users want to accomplish
- **Progressive disclosure** - Use expandable sections for depth
- **Scannable** - Bullet points, tables, clear headings
- **Consistent** - Same structure across similar docs

### Kiro Documentation Standards

Follow Kiro best practices:
- **Evidence-based** - Every claim backed by code/metrics
- **Show, don't tell** - Code examples for concepts
- **Multiple audiences** - Developers, decision makers, users
- **Comprehensive testing** - Document test coverage
- **Real-world focus** - Use cases and impact

## Documentation Philosophy

### 1. Show, Don't Just Tell

- Include code examples for every concept
- Provide mathematical proofs for performance claims
- Use diagrams to illustrate architecture
- Include real metrics and benchmarks

### 2. Multiple Audiences

Write for different reader types:

**Developers:**
- Technical architecture details
- Code examples and patterns
- Performance characteristics
- Testing strategies

**Decision Makers:**
- Business value and ROI
- Use cases and success stories
- Competitive advantages
- Future roadmap

**End Users:**
- Quick start guides
- Troubleshooting tips
- Feature tutorials
- FAQ sections

### 3. Evidence-Based Claims

Every claim must be backed by:
- Code examples
- Test results
- Performance benchmarks
- Real-world metrics

**Example:**
```markdown
❌ "The game is fast"
✅ "The game maintains 60 FPS with 500+ entities through spatial grid 
    optimization that reduces collision checks from O(n²) to O(n)"
```

## Documentation Structure

### Root Directory (Minimal)

**README.md** - Project overview with expandable sections
- What it does, why it matters, quick start
- Expandable sections for deeper content
- Links to full documentation hub

**QUICKSTART.md** - 60-second setup (optional, can be in docs/)
- Minimal steps to run
- Common issues
- Next steps

**BACKLOG.md** - Feature roadmap (project management)
**LICENSE** - License file
**.env.example** - Configuration template

### Documentation Hub (docs/)

**docs/README.md** - Central documentation hub
- Navigation with expandable sections
- Organized by audience and task
- Quick links and search by topic

### Documentation Organization

```
docs/
├── README.md                    # Documentation hub
├── guides/                      # How-to guides
│   ├── QUICKSTART.md
│   ├── INSTALLATION.md
│   ├── CONFIGURATION.md
│   ├── DEVELOPMENT_SETUP.md
│   ├── TESTING.md
│   └── QUESTS.md
├── architecture/                # Technical deep dives
│   ├── ARCHITECTURE.md
│   ├── PERFORMANCE.md
│   ├── PATTERNS.md
│   └── PROJECT_SHOWCASE.md
├── reference/                   # API and reference docs
│   ├── API.md
│   ├── MECHANICS.md
│   ├── CHANGELOG.md
│   ├── TROUBLESHOOTING.md
│   └── PROJECT_SUMMARY.md
├── community/                   # Contributing and collaboration
│   ├── CONTRIBUTING.md
│   ├── DEVELOPMENT.md
│   └── STANDARDS.md
└── sonrai-api/                  # API-specific docs
    ├── README.md
    ├── INTEGRATION_GUIDE.md
    └── queries/
```

### Progressive Disclosure Pattern

Use expandable sections in documentation:

```markdown
## Features

<details>
<summary><b>🚀 Getting Started</b></summary>

- [Quick Start](guides/QUICKSTART.md)
- [Installation](guides/INSTALLATION.md)
- [Configuration](guides/CONFIGURATION.md)

</details>

<details>
<summary><b>🏗️ Architecture</b></summary>

- [System Architecture](architecture/ARCHITECTURE.md)
- [Performance](architecture/PERFORMANCE.md)

</details>
```

This allows:
- **Scannable** - See all topics at a glance
- **Progressive** - Expand only what you need
- **Clean** - Minimal visual clutter
- **Organized** - Clear hierarchy

## Writing Standards

### Code Examples

Always include:
1. **Context** - What problem does this solve?
2. **Code** - Working, tested example
3. **Explanation** - How does it work?
4. **Impact** - What's the result?

**Template:**
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

## Documentation Maintenance

### When to Update

**Always update documentation when:**
- Adding new features
- Fixing bugs
- Changing APIs
- Improving performance
- Refactoring code

### Documentation Checklist

Before marking a feature complete:

- [ ] README.md updated with new feature
- [ ] ARCHITECTURE.md updated if architecture changed
- [ ] API docs updated if API changed
- [ ] Code examples tested and working
- [ ] Metrics and benchmarks included
- [ ] Diagrams updated if needed
- [ ] CHANGELOG.md entry added

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

## Documentation Types

### 1. Tutorial Documentation

**Purpose:** Teach users how to accomplish specific tasks

**Structure:**
1. Goal statement
2. Prerequisites
3. Step-by-step instructions
4. Expected results
5. Troubleshooting

**Example:**
```markdown
## How to Create a Custom Quest

**Goal:** Add a new side quest to the game

**Prerequisites:**
- Python 3.11+
- Understanding of quest state machine
- Familiarity with Sonrai API

**Steps:**
1. Create quest class...
2. Implement state machine...
3. Add API integration...
4. Test quest workflow...

**Expected Result:** New quest appears in specified level

**Troubleshooting:**
- Quest not triggering? Check trigger position
- API errors? Verify credentials
```

### 2. Reference Documentation

**Purpose:** Provide detailed API information

**Structure:**
- Function signature
- Parameters
- Return value
- Exceptions
- Examples

**Example:**
```markdown
### check_collisions()

Check for collisions between projectiles and zombies.

**Signature:**
\`\`\`python
def check_collisions(
    projectiles: List[Projectile],
    zombies: List[Zombie],
    grid: SpatialGrid
) -> List[Tuple[Projectile, Zombie]]
\`\`\`

**Parameters:**
- `projectiles` - List of active projectiles
- `zombies` - List of zombies to check
- `grid` - Spatial grid for optimization

**Returns:**
List of (projectile, zombie) collision pairs

**Example:**
\`\`\`python
collisions = check_collisions(projectiles, zombies, grid)
for proj, zombie in collisions:
    zombie.take_damage(proj.damage)
\`\`\`
```

### 3. Conceptual Documentation

**Purpose:** Explain how systems work

**Structure:**
1. Problem statement
2. Solution approach
3. Implementation details
4. Trade-offs
5. Alternatives considered

**Example:**
```markdown
## Spatial Grid Collision Detection

**Problem:** Checking every projectile against every zombie is O(n²)

**Solution:** Divide world into grid cells, only check nearby cells

**Implementation:**
- 100×100 pixel cells
- Hash map for O(1) cell lookup
- Check 3×3 grid around projectile

**Trade-offs:**
- Memory: O(m) for grid storage
- Optimal cell size depends on entity density

**Alternatives:**
- Quadtree: More complex, similar performance
- Sweep and prune: Better for many projectiles
```

## Quality Standards

### Excellent Documentation Has:

✅ Clear, concise writing
✅ Working code examples
✅ Accurate metrics
✅ Helpful diagrams
✅ Comprehensive coverage
✅ Easy navigation
✅ Regular updates

### Poor Documentation Has:

❌ Vague descriptions
❌ Broken code examples
❌ Outdated information
❌ Missing context
❌ Incomplete coverage
❌ Confusing organization
❌ Stale content

## Tools and Resources

### Documentation Tools

- **Markdown** - All documentation in Markdown
- **LaTeX** - Mathematical formulas
- **Mermaid** - Complex diagrams (if needed)
- **ASCII art** - Simple diagrams

### Validation Tools

```bash
# Check markdown syntax
markdownlint *.md

# Check links
markdown-link-check *.md

# Spell check
aspell check *.md
```

### Documentation Templates

See `docs/templates/` for:
- Feature documentation template
- API documentation template
- Tutorial template
- Troubleshooting template

## Success Metrics

Good documentation should:

1. **Reduce support questions** - Users find answers themselves
2. **Accelerate onboarding** - New contributors productive quickly
3. **Increase adoption** - Clear value proposition attracts users
4. **Enable contributions** - Community can extend the project
5. **Showcase excellence** - Technical sophistication is evident

## Documentation Standards Reference

For complete documentation standards, see:
- **[Documentation Standards](../../docs/DOCUMENTATION_STANDARDS.md)** - Complete standards guide
- **[Documentation Hub](../../docs/README.md)** - Central navigation

## Remember

Documentation is not an afterthought—it's a core deliverable that showcases the project's quality and professionalism. Every line of documentation should demonstrate:

- **Technical Excellence** - Deep understanding of systems
- **Clear Communication** - Complex concepts explained simply
- **Attention to Detail** - Accurate, tested, complete
- **User Focus** - Anticipates needs, solves problems
- **AWS Standards** - Action-oriented, task-focused, progressive disclosure
- **Kiro Standards** - Evidence-based, code examples, multiple audiences

---

**Great documentation makes great projects accessible to everyone.**
