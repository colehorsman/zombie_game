#!/usr/bin/env python3
"""Show which controller the game will use."""

import pygame

pygame.init()
pygame.joystick.init()

print("\n" + "=" * 60)
print("GAME CONTROLLER SELECTION")
print("=" * 60 + "\n")

controller_count = pygame.joystick.get_count()
print(f"Found {controller_count} controller(s)\n")

if controller_count == 0:
    print("❌ No controllers - game will use keyboard only")
else:
    # Simulate game's controller selection logic
    selected = None
    for i in range(controller_count):
        joy = pygame.joystick.Joystick(i)
        joy.init()
        print(f"Controller {i}: {joy.get_name()}")
        if selected is None:
            selected = joy
            print(f"  ✅ SELECTED - Game will use this one")
        else:
            print(f"  ⏭️  Available but not selected")

    print(f"\n🎮 The game will use: {selected.get_name()}")
    print(f"   (Controller 0)")

print("\n" + "=" * 60)
print("To use a different controller:")
print("1. Unplug the one you don't want")
print("2. Or disconnect it in Bluetooth settings")
print("3. The game will automatically use the first available")
print("=" * 60 + "\n")

pygame.quit()
