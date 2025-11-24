# Test Suite

This directory contains unit tests for the Sonrai Zombie Blaster game.

## Running Tests

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test file
python3 -m pytest tests/test_projectile.py -v

# Run with coverage
python3 -m pytest tests/ --cov=src --cov-report=term-missing

# Run with coverage HTML report
python3 -m pytest tests/ --cov=src --cov-report=html
```

## Test Files

- `test_models.py` - Core data models (Vector2, GameState)
- `test_projectile.py` - Projectile physics and movement
- `test_zombie.py` - Zombie entity behavior
- `test_collision.py` - Collision detection system
- `conftest.py` - Shared fixtures and configuration

## Test Status

Current test results:
- ✅ 11 passing tests
- ❌ 9 failing tests (need fixes based on actual API signatures)

## Adding New Tests

When adding tests for new features:

1. **Check the actual source code first** - don't assume API signatures
2. Create a new test file: `test_<module_name>.py`
3. Use descriptive test names: `test_<what_is_being_tested>`
4. Organize tests into classes by functionality
5. Use fixtures from `conftest.py` for common setup
6. Mock external dependencies (pygame, API calls)

## Test Coverage Goals

- Minimum 70% overall coverage
- 90%+ for critical systems (collision, API, scoring)
- 100% for utility functions
