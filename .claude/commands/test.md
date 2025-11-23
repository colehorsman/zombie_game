# Test Command

Launch the game with automated test plan and checklist.

Run the test launcher:
```bash
python test_launcher.py
```

This will:
1. Display the current test plan with objectives
2. Show step-by-step test instructions
3. List success criteria
4. Launch the game automatically
5. Show post-test report

## Options

Test specific features:
```bash
python test_launcher.py --feature powerups      # Test powerup system
python test_launcher.py --feature level_entry   # Test level transitions
python test_launcher.py --feature full          # Full game test
```

Watch logs in real-time:
```bash
python test_launcher.py --watch-logs
```

List available test plans:
```bash
python test_launcher.py --list
```
