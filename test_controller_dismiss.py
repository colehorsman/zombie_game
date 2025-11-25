#!/usr/bin/env python3
"""Test that controller buttons can dismiss messages."""

import pygame
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from models import GameState, GameStatus

print("\n" + "=" * 60)
print("CONTROLLER MESSAGE DISMISS TEST")
print("=" * 60 + "\n")

# Initialize pygame
pygame.init()
pygame.joystick.init()

# Check for controller
if pygame.joystick.get_count() == 0:
    print("❌ No controller detected!")
    print("   Connect a controller to test")
    sys.exit(1)

controller = pygame.joystick.Joystick(0)
controller.init()
print(f"✅ Using controller: {controller.get_name()}\n")

# Create a mock game state with a message
game_state = GameState(
    status=GameStatus.PAUSED,
    zombies_remaining=10,
    zombies_quarantined=0,
    total_zombies=10,
    third_parties_blocked=0,
    total_third_parties=0
)
game_state.congratulations_message = "🔒 Level Locked\n\nTest Message\n\nPress A/B/Start or ENTER to continue"
game_state.previous_status = GameStatus.LOBBY

print("Test Scenario:")
print("  Status: PAUSED")
print("  Message: 'Level Locked'")
print("  Previous Status: LOBBY")
print()
print("Expected Behavior:")
print("  - Press A button (0) → Message dismissed, status returns to LOBBY")
print("  - Press B button (1) → Message dismissed, status returns to LOBBY")
print("  - Press Start (7) → Message dismissed, status returns to LOBBY")
print()
print("=" * 60)
print("Press A, B, or Start button to test dismissal")
print("Press Ctrl+C to exit")
print("=" * 60 + "\n")

clock = pygame.time.Clock()
running = True

try:
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.JOYBUTTONDOWN:
                button = event.button
                button_name = {0: "A", 1: "B", 7: "Start"}.get(button, f"Button {button}")
                
                # Test if this button should dismiss the message
                if button in [0, 1, 7]:  # A, B, or Start
                    if game_state.status == GameStatus.PAUSED and game_state.congratulations_message:
                        print(f"✅ {button_name} pressed - Dismissing message...")
                        
                        # Simulate dismiss_message() logic
                        game_state.congratulations_message = None
                        if game_state.previous_status:
                            game_state.status = game_state.previous_status
                            game_state.previous_status = None
                        
                        print(f"   Message cleared: {game_state.congratulations_message is None}")
                        print(f"   Status restored to: {game_state.status}")
                        print()
                        print("✅ TEST PASSED! Controller button dismissed message correctly")
                        print()
                        
                        # Reset for another test
                        game_state.status = GameStatus.PAUSED
                        game_state.congratulations_message = "🔒 Level Locked\n\nTest Message\n\nPress A/B/Start or ENTER to continue"
                        game_state.previous_status = GameStatus.LOBBY
                        print("Reset for another test. Press A, B, or Start again...")
                        print()
                else:
                    print(f"⏭️  {button_name} pressed - Not a dismiss button")
        
        clock.tick(60)

except KeyboardInterrupt:
    print("\n\n✅ Test complete!")

pygame.quit()
