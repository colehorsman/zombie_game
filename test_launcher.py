#!/usr/bin/env python3
"""
Automated Test Launcher for Sonrai Zombie Blaster

This script displays the current test plan, opens the game,
and optionally tails the logs for real-time debugging.

Usage:
    python test_launcher.py                 # Launch with test plan
    python test_launcher.py --watch-logs    # Launch and tail logs
    python test_launcher.py --feature <name> # Launch for specific feature test
"""

import sys
import os
import subprocess
import argparse
import time
from datetime import datetime


# Test Plans for Different Features
TEST_PLANS = {
    "powerups": {
        "title": "Power-Up System Test",
        "objectives": [
            "Verify powerups spawn in platformer levels",
            "Test Star Power (*) invincibility and touch-quarantine",
            "Test Lambda Speed (λ) 2x movement boost",
            "Verify powerups clear when returning to lobby",
            "Check powerup distribution by difficulty"
        ],
        "steps": [
            "1. Start the game and wait for lobby to load",
            "2. Enter the Sandbox level (walk through door)",
            "3. Look for gold stars (⭐) and orange lambda badges (λ) on platforms",
            "   → Expected: 6-12 powerups visible on platforms",
            "4. Collect a Star Power (gold star):",
            "   → Expected: Screen effect, invincibility message",
            "   → Touch a zombie - should quarantine instantly (no shooting)",
            "   → Effect lasts 10 seconds",
            "5. Collect a Lambda Speed (orange λ):",
            "   → Expected: Movement speed doubles",
            "   → Easier to jump across platforms",
            "   → Effect lasts 12 seconds",
            "6. Return to lobby entrance (walk left to start)",
            "7. Exit to lobby",
            "   → Expected: Powerups cleared, back in lobby",
            "8. Enter Production level",
            "   → Expected: Different powerup distribution (fewer stars)"
        ],
        "log_keywords": ["powerup", "spawn", "star", "lambda", "collected"],
        "success_criteria": [
            "✅ Powerups visible on platforms in levels",
            "✅ Star Power grants invincibility + touch quarantine",
            "✅ Lambda Speed doubles movement speed",
            "✅ Powerups clear when returning to lobby",
            "✅ No errors in logs during powerup spawning/collection"
        ]
    },
    "level_entry": {
        "title": "Level Entry & Transition Test",
        "objectives": [
            "Verify level entry from lobby works",
            "Test zombie loading for specific accounts",
            "Verify player spawns correctly",
            "Check mode transitions (lobby ↔ platformer)"
        ],
        "steps": [
            "1. Start in lobby",
            "2. Walk to Sandbox door and enter",
            "3. Verify platformer level loads with platforms",
            "4. Check zombies are visible and scattered",
            "5. Return to lobby entrance and exit",
            "6. Verify lobby reloads correctly"
        ],
        "log_keywords": ["enter_level", "ENTERING LEVEL", "Step", "SUCCESS"],
        "success_criteria": [
            "✅ Level loads without errors",
            "✅ Zombies appear in correct positions",
            "✅ Player spawns at entrance",
            "✅ Can return to lobby successfully"
        ]
    },
    "full": {
        "title": "Full Game Test",
        "objectives": [
            "Test complete gameplay flow",
            "Verify all systems working together",
            "Check for any crashes or errors"
        ],
        "steps": [
            "1. Start game from lobby",
            "2. Enter Sandbox level",
            "3. Collect powerups",
            "4. Eliminate some zombies",
            "5. Return to lobby",
            "6. Enter different level (Production)",
            "7. Test boss battle if applicable",
            "8. Save and quit",
            "9. Restart and verify save loaded"
        ],
        "log_keywords": ["ERROR", "WARNING", "CRASH", "Exception"],
        "success_criteria": [
            "✅ No crashes during gameplay",
            "✅ All features work as expected",
            "✅ Save/load works correctly",
            "✅ No error messages in logs"
        ]
    }
}


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_section(title, items):
    """Print a formatted section with items."""
    print(f"\n{title}:")
    print("-" * 70)
    for item in items:
        print(f"  {item}")


def display_test_plan(test_name):
    """Display the test plan for the specified test."""
    if test_name not in TEST_PLANS:
        print(f"❌ Unknown test plan: {test_name}")
        print(f"Available tests: {', '.join(TEST_PLANS.keys())}")
        return False

    plan = TEST_PLANS[test_name]

    # Clear screen (works on Unix and Windows)
    os.system('clear' if os.name == 'posix' else 'cls')

    print_header(f"🎮 {plan['title']}")
    print(f"\nTest Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print_section("📋 Test Objectives", plan['objectives'])
    print_section("🔧 Test Steps", plan['steps'])
    print_section("✅ Success Criteria", plan['success_criteria'])

    if plan.get('log_keywords'):
        print(f"\n💡 Tip: Watch for these keywords in logs:")
        print(f"   {', '.join(plan['log_keywords'])}")

    print("\n" + "=" * 70)
    return True


def launch_game(watch_logs=False):
    """Launch the game and optionally tail logs."""
    print("\n🚀 Launching game...")
    print("   Location: src/main.py")
    print("   Press Ctrl+C to stop")

    if watch_logs:
        print("   📊 Log monitoring: ENABLED")

    print("\n" + "-" * 70 + "\n")

    # Give user a moment to read
    time.sleep(2)

    try:
        if watch_logs:
            # Launch with log output visible
            # Use unbuffered output to see logs in real-time
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'

            process = subprocess.Popen(
                [sys.executable, 'src/main.py'],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # Print logs in real-time
            print("📊 GAME LOGS (real-time):")
            print("-" * 70)

            try:
                for line in process.stdout:
                    print(line, end='')
            except KeyboardInterrupt:
                print("\n\n⚠️  Stopping game...")
                process.terminate()
                process.wait()
        else:
            # Launch without log output (cleaner UI)
            subprocess.run([sys.executable, 'src/main.py'])

    except KeyboardInterrupt:
        print("\n\n⚠️  Test session interrupted")
    except Exception as e:
        print(f"\n❌ Error launching game: {e}")
        return False

    return True


def post_test_report():
    """Show post-test report prompt."""
    print("\n" + "=" * 70)
    print("  🎯 Test Session Complete")
    print("=" * 70)
    print("\n📝 Post-Test Questions:")
    print("   • Did all features work as expected?")
    print("   • Were there any errors or crashes?")
    print("   • Did you see any warnings in the logs?")
    print("   • Are there any bugs to report?")
    print("\n💡 Next Steps:")
    print("   • Document any issues found")
    print("   • Check logs for errors: grep ERROR game.log")
    print("   • Update test status in tracking system")
    print("   • Create bug reports for any failures")
    print("\n" + "=" * 70 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Automated test launcher for Sonrai Zombie Blaster",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_launcher.py                      # Test current feature (powerups)
  python test_launcher.py --feature full       # Full game test
  python test_launcher.py --watch-logs         # Show logs in real-time
  python test_launcher.py --feature level_entry --watch-logs
        """
    )

    parser.add_argument(
        '--feature',
        choices=list(TEST_PLANS.keys()),
        default='powerups',
        help='Which feature to test (default: powerups)'
    )

    parser.add_argument(
        '--watch-logs',
        action='store_true',
        help='Display game logs in real-time during testing'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List available test plans'
    )

    args = parser.parse_args()

    # List test plans
    if args.list:
        print("\n📋 Available Test Plans:\n")
        for name, plan in TEST_PLANS.items():
            print(f"  • {name:15} - {plan['title']}")
        print()
        return 0

    # Display test plan
    if not display_test_plan(args.feature):
        return 1

    # Prompt to continue
    try:
        input("\n⏸️  Press ENTER to launch the game (or Ctrl+C to cancel)... ")
    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled")
        return 0

    # Launch game
    success = launch_game(watch_logs=args.watch_logs)

    # Post-test report
    if success:
        post_test_report()

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
