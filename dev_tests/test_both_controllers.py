#!/usr/bin/env python3
"""Test both controllers to make sure they work."""

import pygame
import sys

pygame.init()
pygame.joystick.init()

controller_count = pygame.joystick.get_count()

if controller_count < 2:
    print(f"❌ Only {controller_count} controller(s) detected")
    print("   Need 2 controllers to test both")
    sys.exit(1)

print("\n" + "=" * 60)
print("TESTING BOTH CONTROLLERS")
print("=" * 60 + "\n")

# Initialize both controllers
controllers = []
for i in range(2):
    joy = pygame.joystick.Joystick(i)
    joy.init()
    controllers.append(joy)
    print(f"Controller {i}: {joy.get_name()}")

print("\n" + "=" * 60)
print("Press buttons on EITHER controller to test")
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
                controller = controllers[event.joy]
                print(f"✅ Controller {event.joy} ({controller.get_name()}): Button {event.button} pressed")
            
            elif event.type == pygame.JOYAXISMOTION:
                if abs(event.value) > 0.5:
                    controller = controllers[event.joy]
                    direction = "+" if event.value > 0 else "-"
                    print(f"✅ Controller {event.joy} ({controller.get_name()}): Axis {event.axis} {direction}{abs(event.value):.2f}")
            
            elif event.type == pygame.JOYHATMOTION:
                if event.value != (0, 0):
                    controller = controllers[event.joy]
                    print(f"✅ Controller {event.joy} ({controller.get_name()}): D-Pad {event.value}")
        
        clock.tick(60)

except KeyboardInterrupt:
    print("\n\n✅ Test complete! Both controllers working.")

pygame.quit()
