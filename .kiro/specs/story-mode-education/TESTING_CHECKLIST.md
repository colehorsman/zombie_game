# Story Mode Education - Manual Testing Checklist

## Prerequisites
- Game is running (`python src/main.py`)
- You're in the lobby

## Test 1: Story Mode Activation
1. Walk to any door (e.g., Sandbox)
2. When the mode selection menu appears, select **📖 STORY MODE**
3. **Expected:** You enter the level in Story Mode

## Test 2: First Zombie Kill Education
1. In Story Mode, eliminate your first zombie
2. **Expected:** A dialogue bubble appears with:
   - "You just quarantined [zombie_name]!"
   - Information about the zombie type and days since login
   - Explanation of Cloud Permissions Firewall
3. Press A/ENTER/SPACE to advance through pages
4. **Expected:** Dialogue dismisses after viewing all pages

## Test 3: First Role Encounter
1. Eliminate a zombie that is a "Role" type
2. **Expected:** A dialogue appears explaining:
   - "You encountered a Role-type zombie!"
   - Explanation that Roles are used by services/applications
   - Warning about unused roles having broad permissions

## Test 4: First User Encounter
1. Eliminate a zombie that is a "User" type
2. **Expected:** A dialogue appears explaining:
   - "You encountered a User-type zombie!"
   - Explanation that Users are human accounts
   - Information about zombie accounts from departed employees

## Test 5: Milestone - 5 Kills
1. Eliminate 5 zombies total
2. **Expected:** A dialogue appears:
   - "5 zombies quarantined! You're making progress!"
   - Information about identity audits

## Test 6: Milestone - 10 Kills
1. Eliminate 10 zombies total
2. **Expected:** A dialogue appears:
   - "10 zombies eliminated! You're a security champion!"
   - Information about attack surface reduction

## Test 7: Level Completion
1. Eliminate all zombies in a level
2. Defeat the boss
3. **Expected:** A dialogue appears:
   - "Level Complete!"
   - Summary of security concepts learned

## Test 8: Dialogue Pauses Gameplay
1. When a dialogue is active, try to move
2. **Expected:** Player cannot move while dialogue is shown
3. Press A/ENTER/SPACE to dismiss
4. **Expected:** Player can move again

## Test 9: Education Not Repeated
1. After seeing the "First Zombie Kill" education, eliminate another zombie
2. **Expected:** The first kill education does NOT appear again
3. Same for Role/User encounters - they only trigger once

## Test 10: Arcade Mode Has No Education
1. Return to lobby
2. Enter a level and select **🕹️ ARCADE MODE**
3. Eliminate zombies
4. **Expected:** No educational dialogues appear in Arcade Mode

## Test 11: Progress Persists
1. Play Story Mode and trigger some education
2. Return to lobby
3. Re-enter Story Mode
4. **Expected:** Previously seen education does NOT repeat

## Known Limitations
- AWS Permission Display (Tasks 10-11) not yet implemented
- Tutorial Reset option (Task 12) not yet implemented

## Test Results

| Test | Pass/Fail | Notes |
|------|-----------|-------|
| 1. Story Mode Activation | | |
| 2. First Zombie Kill | | |
| 3. First Role Encounter | | |
| 4. First User Encounter | | |
| 5. Milestone 5 Kills | | |
| 6. Milestone 10 Kills | | |
| 7. Level Completion | | |
| 8. Dialogue Pauses | | |
| 9. No Repeat Education | | |
| 10. Arcade No Education | | |
| 11. Progress Persists | | |

## Automated Tests
Run: `python -m pytest tests/test_dialogue_system.py -v`
Expected: 25 tests pass
