# Contributing to Sonrai Zombie Blaster

Welcome! This guide will get you from zero to productive in under an hour.

## Quick Start (5 Minutes)

### 1. Prerequisites
- Python 3.11+ installed
- Git installed
- 10 GB free disk space

### 2. Clone & Setup
```bash
# Clone repository
git clone https://github.com/colehorsman/zombie_game.git
cd zombie_game

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 3. Configure Credentials
Edit `.env` and add your Sonrai credentials:
```bash
SONRAI_API_URL=https://your-org.sonraisecurity.com/graphql
SONRAI_ORG_ID=your_org_id
SONRAI_API_TOKEN=your_api_token
```

**Don't have credentials?** Contact the maintainers for sandbox access.

### 4. Run the Game
```bash
python3 src/main.py
```

**Expected:** Game window opens, you see the lobby.

### 5. Run Tests
```bash
pytest tests/ -v
```

**Expected:** Most tests pass (some require specific Sonrai data).

---

## Development Workflow

### Making Changes

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make Your Changes**
   - Edit code in `src/`
   - Add tests in `tests/`
   - Update docs if needed

3. **Test Your Changes**
   ```bash
   # Run specific test file
   pytest tests/test_my_feature.py -v

   # Run all tests
   pytest tests/ -v

   # Run with coverage
   pytest tests/ --cov=src
   ```

4. **Lint and Format**
   ```bash
   # Pre-commit hooks run automatically
   git add .
   git commit -m "feat: add my feature"

   # Or run manually
   pre-commit run --all-files
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/my-feature
   # Then create PR on GitHub
   ```

---

## Common Tasks

### Add a New Entity
1. Create entity class in `src/` (e.g., `src/my_entity.py`)
2. Add to `GameState` in `src/models.py`
3. Implement collision detection in `src/collision.py`
4. Add rendering logic in `src/renderer.py`
5. Write tests in `tests/test_my_entity.py`

**Example:** See `src/zombie.py` and `tests/test_zombie.py`

### Add a New Quest
1. Create quest class in `src/` (e.g., `src/my_quest.py`)
2. Follow pattern from `src/service_protection_quest.py`
3. Add quest state to `GameState` in `src/models.py`
4. Integrate in `src/game_engine.py`
5. Write tests in `tests/test_my_quest.py`

**Example:** See `.kiro/specs/jit-access-quest/`

### Add a New Level
1. Add account to `assets/aws_accounts.csv`
2. Create door in lobby (automatic)
3. Configure difficulty in `src/difficulty_config.py`
4. Test with real Sonrai data

---

## Project Structure

```
sonrai-zombie-blaster/
├── src/                      # Main source code
│   ├── main.py              # Entry point
│   ├── game_engine.py       # Core game loop
│   ├── renderer.py          # Graphics rendering
│   ├── models.py            # Data models
│   ├── player.py            # Player character
│   ├── zombie.py            # Zombie entities
│   ├── sonrai_client.py     # Sonrai API integration
│   └── ...
├── tests/                    # Test files
├── assets/                   # Game assets
├── docs/                     # Documentation
├── .kiro/                    # Kiro AI configuration
└── requirements.txt          # Python dependencies
```

---

## Code Style

### Python Style
- Follow PEP 8
- Use type hints
- Max line length: 100 characters
- Use docstrings for public methods

**Example:**
```python
def calculate_damage(base_damage: int, multiplier: float) -> int:
    """
    Calculate final damage with multiplier.

    Args:
        base_damage: Base damage value
        multiplier: Damage multiplier

    Returns:
        Final damage amount
    """
    return int(base_damage * multiplier)
```

### Commit Messages
Follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring
- `perf:` Performance improvement

**Example:**
```
feat(arcade): add combo multiplier system

Implements 1.5x multiplier when combo reaches 5+.
Includes visual feedback and sound effects.

Closes #42
```

### Branch Naming
- `feature/feature-name` - New features
- `fix/bug-description` - Bug fixes
- `refactor/what-changed` - Refactoring
- `docs/what-documented` - Documentation

---

## Testing Guidelines

### Writing Tests

**Unit Tests:**
```python
def test_zombie_takes_damage():
    """Test zombie health decreases when damaged."""
    zombie = Zombie(x=100, y=100)
    initial_health = zombie.health

    zombie.take_damage(10)

    assert zombie.health == initial_health - 10
```

**Integration Tests:**
```python
def test_quest_completion_workflow():
    """Test complete quest workflow from start to finish."""
    game_state = GameState()
    quest = ServiceProtectionQuest(game_state)

    # Initialize quest
    quest.initialize()
    assert quest.is_active

    # Complete objectives
    quest.protect_service("nOps")
    quest.protect_service("Cloudflare")

    # Verify completion
    assert quest.is_complete
```

### Test Coverage

Aim for:
- **Unit tests:** > 80% coverage
- **Integration tests:** Key workflows
- **Edge cases:** Error handling, boundary conditions

---

## Troubleshooting

### Common Issues

**Problem:** `ModuleNotFoundError: No module named 'pygame'`
**Solution:**
```bash
pip install -r requirements.txt
```

**Problem:** `401 Unauthorized` when loading zombies
**Solution:** Check `.env` file has correct Sonrai credentials

**Problem:** Game running slow (< 30 FPS)
**Solution:**
- Check zombie count (should be < 500)
- Disable debug logging
- Close other applications

**More issues?** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## Getting Help

### Resources
- **Documentation:** [docs/README.md](docs/README.md)
- **Architecture:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **API Guide:** [docs/sonrai-api/README.md](docs/sonrai-api/README.md)
- **Kiro Specs:** [.kiro/specs/](.kiro/specs/)

### Contact
- **Questions:** Open a GitHub issue
- **Bugs:** Use bug report template
- **Features:** Use feature request template

---

## What to Work On

### Good First Issues
Look for issues labeled `good-first-issue`:
- Documentation improvements
- Test coverage
- Bug fixes
- Small features

### Current Priorities
See [.kiro/BACKLOG.md](.kiro/BACKLOG.md) for:
- P0: Critical issues
- P1: High priority features
- P2: Nice-to-have improvements

---

## Code Review Process

### Before Submitting PR

- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No secrets in code

### PR Review Checklist

Reviewers will check:
- [ ] Code quality and readability
- [ ] Test coverage
- [ ] Performance impact
- [ ] Security considerations
- [ ] Documentation completeness

---

## Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes
- Git commit history

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## Thank You! 🎮🚀

Thank you for contributing to Sonrai Zombie Blaster! Your help makes cloud security education accessible and fun for everyone.

**Questions?** Open an issue or reach out to the maintainers.
