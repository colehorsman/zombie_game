#!/usr/bin/env python3
"""Quick D-pad test - shows all button and hat events."""
import pygame
import sys

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No controller!")
    sys.exit(1)

j = pygame.joystick.Joystick(0)
j.init()

print(f"Controller: {j.get_name()}")
print(f"Buttons: {j.get_numbuttons()}")
print(f"Hats: {j.get_numhats()}")
print("\nPress D-pad buttons now...\n")

screen = pygame.display.set_mode((300, 200))
clock = pygame.time.Clock()

for _ in range(1800):  # 30 seconds
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            break
        elif event.type == pygame.JOYBUTTONDOWN:
            print(f"BUTTON DOWN: {event.button}")
        elif event.type == pygame.JOYBUTTONUP:
            print(f"BUTTON UP: {event.button}")
        elif event.type == pygame.JOYHATMOTION:
            print(f"HAT MOTION: {event.value}")

    # Flush output
    sys.stdout.flush()
    clock.tick(60)

pygame.quit()
print("\nTest complete!")
