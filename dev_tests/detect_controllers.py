#!/usr/bin/env python3
"""Quick controller detection script."""

import pygame

pygame.init()
pygame.joystick.init()

print("=" * 60)
print("CONTROLLER DETECTION")
print("=" * 60)

controller_count = pygame.joystick.get_count()
print(f"\n✅ Found {controller_count} controller(s) connected\n")

if controller_count == 0:
    print("❌ No controllers detected!")
    print("\nTroubleshooting:")
    print("1. Make sure controller is connected")
    print("2. Try unplugging and replugging")
    print("3. Check if controller is charged/powered on")
else:
    for i in range(controller_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        
        print(f"Controller {i}:")
        print(f"  Name: {joystick.get_name()}")
        print(f"  Axes: {joystick.get_numaxes()}")
        print(f"  Buttons: {joystick.get_numbuttons()}")
        print(f"  Hats: {joystick.get_numhats()}")
        print(f"  GUID: {joystick.get_guid()}")
        print()

print("\nPress any button on your controller to test...")
print("(Press Ctrl+C to exit)")

# Test input
clock = pygame.time.Clock()
running = True

try:
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.JOYBUTTONDOWN:
                joy = pygame.joystick.Joystick(event.joy)
                print(f"✅ Button {event.button} pressed on '{joy.get_name()}'")
            
            elif event.type == pygame.JOYAXISMOTION:
                if abs(event.value) > 0.5:  # Ignore small movements
                    joy = pygame.joystick.Joystick(event.joy)
                    print(f"✅ Axis {event.axis} moved to {event.value:.2f} on '{joy.get_name()}'")
            
            elif event.type == pygame.JOYHATMOTION:
                if event.value != (0, 0):
                    joy = pygame.joystick.Joystick(event.joy)
                    print(f"✅ D-Pad moved to {event.value} on '{joy.get_name()}'")
        
        clock.tick(60)

except KeyboardInterrupt:
    print("\n\n✅ Test complete!")

pygame.quit()
