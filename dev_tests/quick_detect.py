#!/usr/bin/env python3
"""Quick controller detection - just shows what's connected."""

import sys

import pygame

pygame.init()
pygame.joystick.init()

print("\n" + "=" * 60)
print("CONTROLLER DETECTION")
print("=" * 60 + "\n")

controller_count = pygame.joystick.get_count()
print(f"Found {controller_count} controller(s) connected\n")

if controller_count == 0:
    print("❌ No controllers detected!")
    print("\nMake sure your controller is:")
    print("  - Plugged in (wired) or paired (wireless)")
    print("  - Powered on")
    print("  - Recognized by your system")
    sys.exit(1)

for i in range(controller_count):
    joystick = pygame.joystick.Joystick(i)
    joystick.init()

    print(f"Controller {i}:")
    print(f"  ✅ Name: {joystick.get_name()}")
    print(f"  📊 Axes: {joystick.get_numaxes()}")
    print(f"  🔘 Buttons: {joystick.get_numbuttons()}")
    print(f"  🎮 D-Pads: {joystick.get_numhats()}")
    print(f"  🆔 GUID: {joystick.get_guid()}")
    print()

print("✅ All controllers detected successfully!")
print("\nTo test button presses, run: python3 dev_tests/quick_controller_test.py")

pygame.quit()
