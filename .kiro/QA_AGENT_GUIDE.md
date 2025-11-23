# QA Testing Agent Guide

This document explains how to use the dedicated QA Testing Agent for the Sonrai Zombie Blaster game.

## Overview

The QA Testing Agent is a specialized Kiro agent focused exclusively on testing, quality assurance, and ensuring functionality. It uses custom steering rules and hooks to maintain high code quality.

## Activating the QA Agent

To activate the QA Testing Agent in any conversation, use the steering context:

```
#qa-testing-agent
```

This will load the QA-specific guidelines and focus the agent on testing tasks.

## Available Hooks

### 1. QA Review (Manual)
**Purpose**: Comprehensive QA review of recent changes  
**How to use**: Click "QA Review" in the Agent Hooks panel  
**What it does**:
- Reviews recent code changes
- Identifies missing test coverage
- Runs existing tests
- Suggests new tests
- Verifies critical functionality

### 2. Test API Integration (Manual)
**Purpose**: Test all Sonrai API integration scenarios  
**How to use**: Click "Test API Integration" in the Agent Hooks panel  
**What it does**:
- Tests successful API calls
- Tests failure scenarios (auth, network, rate limiting)
- Verifies error handling
- Ensures proper mocking in tests

### 3. Test Game Mechanics (Manual)
**Purpose**: Test core game systems  
**How to use**: Click "Test Game Mechanics" in the Agent Hooks panel  
**What it does**:
- Tests collision detection
- Tests movement systems
- Tests scoring and progression
- Tests health and damage systems

### 4. Generate Coverage Report (Manual)
**Purpose**: Generate detailed test coverage report  
**How to use**: Click "Generate Coverage Report" in the Agent Hooks panel  
**What it does**:
- Runs pytest with coverage analysis
- Generates HTML coverage report
- Shows which lines are not covered by tests

### 5. Run Tests on Save (Automatic - Disabled by default)
**Purpose**: Auto-run tests when saving Python files  
**How to use**: Enable in Agent Hooks panel  
**What it does**:
- Watches for changes to src/**/*.py files
- Automatically runs pytest when files are saved
- Provides immediate feedback on test failures

## Typical QA Workflow

### 1. After Implementing a New Feature

```
Hey Kiro, I just implemented [feature name]. Can you use #qa-testing-agent 
to review the code and create comprehensive tests for it?
```

### 2. Before Committing Code

```
#qa-testing-agent Please run a full QA review before I commit. 
Check test coverage and run all tests.
```

### 3. When Fixing a Bug

```
#qa-testing-agent I fixed a bug in [component]. Can you create a 
regression test to ensure this bug doesn't come back?
```

### 4. Regular Quality Checks

Use the manual hooks:
1. Click "QA Review" weekly
2. Click "Test API Integration" after API changes
3. Click "Test Game Mechanics" after gameplay changes
4. Click "Generate Coverage Report" to track progress

## Test Organization

```
tests/
├── test_player.py          # Player movement and controls
├── test_zombie.py          # Zombie behavior
├── test_projectile.py      # Projectile system
├── test_collision.py       # Collision detection
├── test_game_engine.py     # Game state management
├── test_sonrai_client.py   # API integration
├── test_scoring.py         # Scoring and multipliers
└── test_level_progression.py  # Level system
```

## Running Tests Manually

### Run all tests:
```bash
pytest tests/
```

### Run specific test file:
```bash
pytest tests/test_collision.py
```

### Run with coverage:
```bash
pytest --cov=src tests/
```

### Run with detailed output:
```bash
pytest -v tests/
```

### Run only failed tests:
```bash
pytest --lf tests/
```

## Coverage Goals

- **Minimum**: 70% overall coverage
- **Critical systems**: 90%+ coverage (collision, API, scoring)
- **Utility functions**: 100% coverage

## Best Practices

1. **Always use #qa-testing-agent** when asking for testing help
2. **Run tests before committing** code changes
3. **Create tests for bug fixes** to prevent regressions
4. **Keep tests fast** - unit tests should run in milliseconds
5. **Mock external dependencies** - especially API calls and pygame
6. **Use descriptive test names** - explain what is being tested
7. **Test edge cases** - empty inputs, boundaries, error conditions

## Example QA Agent Interactions

### Request comprehensive testing:
```
#qa-testing-agent I need you to test the new damage system. 
Create unit tests for:
- Damage application
- Health tracking
- Entity elimination
- Damage multiplier calculations

Run the tests and report any issues.
```

### Request API testing:
```
#qa-testing-agent Please test the Sonrai API client. 
I want to ensure we handle:
- Network timeouts
- Authentication failures
- Rate limiting
- Invalid responses

Create mocked tests for all scenarios.
```

### Request regression testing:
```
#qa-testing-agent I fixed a bug where projectiles weren't 
hitting zombies correctly. Can you create a regression test 
to ensure this specific scenario works?
```

## Troubleshooting

### Tests are failing
1. Use #qa-testing-agent to analyze failures
2. Check if it's a test issue or code issue
3. Review test output for specific errors

### Low test coverage
1. Run "Generate Coverage Report" hook
2. Use #qa-testing-agent to identify untested code
3. Request tests for specific modules

### Flaky tests
1. Use #qa-testing-agent to identify non-deterministic behavior
2. Check for timing issues or missing mocks
3. Ensure tests don't depend on external state

## Integration with Development

The QA Agent works alongside your development workflow:

1. **Development Agent**: Implements features
2. **QA Agent**: Tests features and finds bugs
3. **Development Agent**: Fixes bugs found by QA
4. **QA Agent**: Verifies fixes with regression tests

## Continuous Improvement

Regularly ask the QA Agent to:
- Review test quality
- Suggest testing improvements
- Identify gaps in coverage
- Recommend better testing patterns

---

**Remember**: The QA Agent is your quality guardian. Use it frequently to maintain high code quality and catch bugs early!
