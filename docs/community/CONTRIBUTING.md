# Contributing to Sonrai Zombie Blaster

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in all interactions.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Sonrai Security account (for API testing)
- Basic understanding of Pygame and game development

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/zombie_game.git
   cd zombie_game
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Sonrai credentials
   ```

5. **Run tests**
   ```bash
   pytest
   ```

6. **Run the game**
   ```bash
   python3 src/main.py
   ```

## Development Workflow

### Branch Strategy

- `main` - Production-ready code
- `v2` - Current development branch (hybrid mode)
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Critical production fixes

### Creating a Feature Branch

```bash
# Update your fork
git checkout v2
git pull upstream v2

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: add your feature description"

# Push to your fork
git push origin feature/your-feature-name
```

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(collision): implement spatial grid optimization
fix(quest): reset zombie flags on quest completion
docs(api): add GraphQL query examples
test(arcade): add menu navigation tests
```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length:** 120 characters (not 79)
- **Indentation:** 4 spaces
- **Quotes:** Double quotes for strings
- **Type hints:** Required for public APIs

### Code Formatting

```bash
# Format code with black
black src/ tests/

# Sort imports
isort src/ tests/

# Check style
flake8 src/ tests/
```

### Documentation Standards

**Module Docstrings:**
```python
"""Module for handling collision detection.

This module implements spatial grid partitioning for efficient
collision detection between projectiles and entities.
"""
```

**Function Docstrings:**
```python
def check_collisions(projectiles: List[Projectile], 
                     zombies: List[Zombie]) -> List[Tuple]:
    """
    Check for collisions between projectiles and zombies.
    
    Args:
        projectiles: List of active projectiles
        zombies: List of zombies to check against
        
    Returns:
        List of (projectile, zombie) collision pairs
        
    Example:
        >>> collisions = check_collisions(projectiles, zombies)
        >>> for proj, zombie in collisions:
        ...     zombie.take_damage(proj.damage)
    """
```

### Code Organization

**File Structure:**
```python
# 1. Imports (standard library, third-party, local)
import logging
from typing import List, Optional

import pygame

from models import Vector2, GameState

# 2. Constants
GRAVITY = 980  # pixels/second²
MAX_VELOCITY = 400

# 3. Classes
class Player:
    """Player character with physics and controls."""
    
    def __init__(self, position: Vector2):
        self.position = position
        
    def update(self, delta_time: float):
        """Update player state."""
        pass

# 4. Functions
def create_player(x: float, y: float) -> Player:
    """Factory function for creating players."""
    return Player(Vector2(x, y))
```

## Testing Requirements

### Test Coverage

- **Minimum coverage:** 80% for new code
- **Critical paths:** 100% coverage required
- **Integration tests:** Required for API interactions

### Writing Tests

**Unit Test Example:**
```python
def test_zombie_takes_damage():
    """Test that zombie health decreases when taking damage."""
    zombie = Zombie("z1", "TestZombie", Vector2(100, 100), "account")
    
    initial_health = zombie.health
    zombie.take_damage(1)
    
    assert zombie.health == initial_health - 1
```

**Integration Test Example:**
```python
def test_quest_completion_workflow(game_engine):
    """Test complete quest workflow from trigger to completion."""
    # Setup
    game_engine.arcade_manager.start_session()
    
    # Trigger quest
    game_engine.player.position.x = 300
    game_engine._update_quests(0.016)
    
    # Verify quest triggered
    quest = game_engine.quest_manager.get_quest_for_level(1)
    assert quest.status == QuestStatus.TRIGGERED
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_collision.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run only fast tests
pytest -m "not slow"

# Run with verbose output
pytest -v
```

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] No merge conflicts with target branch

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots for visual changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass locally
```

### Review Process

1. **Automated Checks**
   - Tests must pass
   - Code coverage must meet minimum
   - Style checks must pass

2. **Code Review**
   - At least one approval required
   - Address all review comments
   - Maintain constructive dialogue

3. **Merge**
   - Squash commits for clean history
   - Update CHANGELOG.md
   - Delete feature branch after merge

## Areas for Contribution

### High Priority

- **Bug Fixes** - See [BACKLOG.md](BACKLOG.md) for open issues
- **Performance Optimization** - Profile and optimize hot paths
- **Test Coverage** - Increase coverage for critical modules
- **Documentation** - Improve API docs and examples

### Feature Ideas

- **New Quests** - S3 protection, RDS protection, etc.
- **Power-Ups** - New AWS-themed power-ups
- **Boss Battles** - Cyber-themed boss encounters
- **Multiplayer** - Co-op gameplay
- **VR Mode** - Virtual reality support

### Documentation

- **Tutorials** - Step-by-step guides
- **API Examples** - More GraphQL query examples
- **Architecture Docs** - Deep dives into systems
- **Video Tutorials** - Gameplay and development guides

## Community

### Communication Channels

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - General questions and ideas
- **Pull Requests** - Code contributions

### Getting Help

- Check [README.md](README.md) for basic information
- Search existing issues before creating new ones
- Provide detailed information in bug reports
- Be patient and respectful

### Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

## Development Tips

### Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use debug mode
LOG_LEVEL=DEBUG python3 src/main.py
```

### Performance Profiling

```python
# Profile code
python3 -m cProfile -o profile.stats src/main.py

# Analyze results
python3 -m pstats profile.stats
```

### Testing with Real API

```bash
# Use test account
export SONRAI_API_URL=https://test-org.sonraisecurity.com/graphql

# Enable API logging
export API_DEBUG=true
```

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to open an issue or start a discussion. We're here to help!

---

**Thank you for contributing to Sonrai Zombie Blaster!** 🎮🧟‍♂️🛡️
