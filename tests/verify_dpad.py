#!/usr/bin/env python3
"""Verify D-pad button mapping."""
import pygame
import sys

pygame.init()
pygame.joystick.init()

j = pygame.joystick.Joystick(0)
j.init()

print("Press each D-pad button ONE at a time:")
print("1. D-pad UP")
print("2. D-pad DOWN")
print("3. D-pad LEFT")
print("4. D-pad RIGHT")
print("\n(Press any other button to exit)\n")

screen = pygame.display.set_mode((400, 100))
pygame.display.set_caption("D-pad Mapper - Press D-pad buttons")
clock = pygame.time.Clock()

mapping = {}
directions = ["UP", "DOWN", "LEFT", "RIGHT"]
current_dir = 0

while current_dir < 4:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
        elif event.type == pygame.JOYBUTTONDOWN:
            button = event.button
            if current_dir < 4:
                print(f"D-pad {directions[current_dir]} = Button {button}")
                mapping[directions[current_dir]] = button
                current_dir += 1
                if current_dir < 4:
                    print(f"\nNow press D-pad {directions[current_dir]}...")

    clock.tick(60)

print("\n✅ Mapping complete!")
print(f"UP={mapping.get('UP')}, DOWN={mapping.get('DOWN')}, LEFT={mapping.get('LEFT')}, RIGHT={mapping.get('RIGHT')}")
pygame.quit()
