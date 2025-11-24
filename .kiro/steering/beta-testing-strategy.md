# Beta Testing Strategy

## Overview

This document outlines the automated testing strategy that simulates actual gameplay scenarios. This bridges the gap between unit tests (QA Tester) and manual gameplay testing.

## Testing Layers

### Layer 1: Unit Tests (QA Tester)
**Location:** `tests/test_sonrai_jit.py`
**Purpose:** Test individual API methods and functions
**Coverage:** 
- API success/failure scenarios
- Error handling
- Data validation
- Mock external dependencies

**Example:**
```python
def test_fetch_permission_sets_success():
    # Test that API method correctly fetches and filters permission sets
```

### Layer 2: Integration Tests (Beta Tester)
**Location:** `tests/test_jit_quest_integration.py`
**Purpose:** Simulate actual gameplay scenarios end-to-end
**Coverage:**
- Quest initialization workflow
- Player interaction sequences
- Success/failure conditions
- Edge cases in gameplay context

**Example:**
```python
def test_scenario_2_player_protects_admin_role():
    # Simulate: Player walks into admin role → API call → Role protected
```

### Layer 3: Manual Testing (Human Tester)
**Location:** Game launch with `python3 src/main.py`
**Purpose:** Verify visual elements, UX, and real API integration
**Coverage:**
- Visual rendering (crowns, shields, auditor)
- Player controls and feel
- Real Sonrai API calls
- Performance and bugs

## Integration Test Scenarios

### Scenario 1: Quest Initialization
**Tests:** Quest appears in production accounts with unprotected roles
**Validates:** API queries, data parsing, entity creation

### Scenario 2: Player Interaction
**Tests:** Player touches admin role → JIT protection applied
**Validates:** Collision detection, API calls, state updates

### Scenario 3: Quest Completion
**Tests:** All roles protected → Success message
**Validates:** Progress tracking, completion logic

### Scenario 4: Quest Failure
**Tests:** Player leaves early → Failure message
**Validates:** Exit handling, failure detection

### Scenario 5: No Quest (Already Protected)
**Tests:** Quest doesn't appear when all roles have JIT
**Validates:** Pre-condition checking

### Scenario 6: No Quest (Non-Production)
**Tests:** Quest doesn't appear in Sandbox/Stage accounts
**Validates:** Account filtering

### Scenario 7: Auditor Behavior
**Tests:** Auditor patrols within boundaries
**Validates:** Entity movement, boundary detection

### Edge Cases
- API errors during JIT application
- Empty permission sets response
- Network timeouts
- Invalid data handling

## Workflow: QA → Beta → Manual

### Step 1: QA Tester Validates Code
```bash
pytest tests/test_sonrai_jit.py -v
```
**Result:** 15/15 unit tests pass
**Validates:** API methods work correctly in isolation

### Step 2: Beta Tester Simulates Gameplay
```bash
pytest tests/test_jit_quest_integration.py -v
```
**Result:** 10/10 scenario tests pass
**Validates:** Feature works correctly in gameplay context

### Step 3: Human Tests Real Game
```bash
python3 src/main.py
# Use UNLOCK cheat code
# Enter production account
# Test JIT quest
```
**Result:** Visual confirmation, UX validation, real API testing
**Validates:** Everything works together in production

## Benefits of This Approach

### 1. Fast Feedback Loop
- Unit tests run in 0.26s
- Integration tests run in 0.32s
- Catch issues before manual testing

### 2. Regression Prevention
- Tests document expected behavior
- Prevent breaking existing features
- Safe refactoring

### 3. Scenario Documentation
- Tests serve as executable documentation
- Show how features should work
- Onboarding for new developers

### 4. Confidence Before Demo
- All tests passing = feature ready
- Reduce manual testing time
- Focus manual testing on UX/visuals

## Future Enhancements

### Automated Visual Testing
Could add screenshot comparison tests:
```python
def test_admin_role_rendering():
    # Render admin role
    # Compare screenshot to baseline
    # Detect visual regressions
```

### Performance Testing
Could add performance benchmarks:
```python
def test_quest_initialization_performance():
    # Time quest initialization
    # Assert < 100ms
```

### Full Game Simulation
Could create a bot that plays through levels:
```python
class GameBot:
    def play_level(self, level_name):
        # Navigate to door
        # Enter level
        # Complete objectives
        # Return to lobby
```

## Running All Tests

### Quick Test (Unit + Integration)
```bash
pytest tests/test_sonrai_jit.py tests/test_jit_quest_integration.py -v
```

### Full Test Suite
```bash
pytest tests/ -v
```

### With Coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

## Test Maintenance

### When to Update Tests

1. **Adding new features** - Add new scenario tests
2. **Fixing bugs** - Add regression test
3. **Changing behavior** - Update affected tests
4. **Refactoring** - Tests should still pass

### Test Quality Checklist

- [ ] Tests are independent (can run in any order)
- [ ] Tests are fast (< 1 second each)
- [ ] Tests are clear (descriptive names and comments)
- [ ] Tests cover happy path and edge cases
- [ ] Tests use mocks for external dependencies
- [ ] Tests validate behavior, not implementation

## Summary

The **Beta Testing Strategy** provides automated scenario-based testing that simulates real gameplay without requiring manual testing or launching the game. This gives confidence that features work correctly before manual validation, saving time and catching issues early.

**Test Pyramid:**
```
        /\
       /  \  Manual Testing (Visual, UX, Real API)
      /____\
     /      \  Integration Tests (Gameplay Scenarios)
    /________\
   /          \  Unit Tests (API Methods, Functions)
  /__________\
```

All layers work together to ensure quality and reliability.
