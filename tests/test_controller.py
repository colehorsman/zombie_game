#!/usr/bin/env python3
"""Test controller input to see what buttons/axes are being pressed."""
import pygame
import sys

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No controller detected!")
    sys.exit(1)

joystick = pygame.joystick.Joystick(0)
joystick.init()

print(f"Controller: {joystick.get_name()}")
print(f"Buttons: {joystick.get_numbuttons()}")
print(f"Axes: {joystick.get_numaxes()}")
print(f"Hats: {joystick.get_numhats()}")
print("\nPress buttons/move sticks/d-pad on your controller...")
print("Press Ctrl+C to exit\n")

# Create a small window (required for event loop)
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Controller Test")

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.JOYBUTTONDOWN:
            print(f"BUTTON DOWN: {event.button}")
        elif event.type == pygame.JOYBUTTONUP:
            print(f"BUTTON UP: {event.button}")
        elif event.type == pygame.JOYAXISMOTION:
            if abs(event.value) > 0.1:  # Only show significant movement
                print(f"AXIS {event.axis}: {event.value:.2f}")
        elif event.type == pygame.JOYHATMOTION:
            print(f"HAT: {event.value}")

    # Also continuously show current axis values
    screen.fill((0, 0, 0))

    clock.tick(60)

pygame.quit()
