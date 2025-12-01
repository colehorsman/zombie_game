#!/usr/bin/env python3
"""Generate a zombie icon matching the in-game zombie sprites"""
import os

import pygame

pygame.init()

# Create a 512x512 icon (will be scaled down for desktop)
size = 512
scale = size // 40  # Original zombie is 40x40

sprite = pygame.Surface((size, size), pygame.SRCALPHA)

# Color palette - Fresh Walker (most recognizable)
SKIN_GREY = (120, 130, 115)  # Greyish-green skin
DARK_GREY = (80, 90, 75)  # Shadow areas
BLOOD_RED = (139, 0, 0)  # Fresh blood
DARK_RED = (100, 0, 0)  # Dark blood
SHIRT_BLUE = (60, 80, 120)  # Torn blue shirt
PANTS_BROWN = (70, 60, 50)  # Brown pants
BLACK = (0, 0, 0)
WHITE_EYE = (230, 230, 220)  # Milky white eyes


def draw_scaled_rect(surface, color, rect, outline=0):
    x, y, w, h = rect
    scaled_rect = (x * scale, y * scale, w * scale, h * scale)
    pygame.draw.rect(surface, color, scaled_rect, outline * scale if outline else 0)


def draw_scaled_circle(surface, color, pos, radius):
    x, y = pos
    pygame.draw.circle(surface, color, (x * scale, y * scale), radius * scale)


# Head
draw_scaled_rect(sprite, SKIN_GREY, (10, 4, 20, 14))
draw_scaled_rect(sprite, BLACK, (10, 4, 20, 14), 1)
draw_scaled_rect(sprite, DARK_GREY, (11, 6, 6, 8))

# Eyes (milky white)
draw_scaled_rect(sprite, WHITE_EYE, (12, 8, 6, 5))
draw_scaled_rect(sprite, WHITE_EYE, (22, 8, 6, 5))
draw_scaled_rect(sprite, BLACK, (14, 9, 2, 3))
draw_scaled_rect(sprite, BLACK, (24, 9, 2, 3))

# Bite wound
draw_scaled_circle(sprite, DARK_RED, (12, 17), 3)
draw_scaled_circle(sprite, BLOOD_RED, (13, 17), 2)

# Body - torn shirt
draw_scaled_rect(sprite, SHIRT_BLUE, (8, 18, 24, 14))
draw_scaled_rect(sprite, BLACK, (8, 18, 24, 14), 1)
draw_scaled_rect(sprite, SKIN_GREY, (12, 22, 4, 6))

# Blood stains
draw_scaled_circle(sprite, DARK_RED, (18, 24), 3)
draw_scaled_circle(sprite, BLOOD_RED, (24, 28), 4)

# Arms reaching forward
draw_scaled_rect(sprite, SKIN_GREY, (2, 18, 6, 12))
draw_scaled_rect(sprite, BLACK, (2, 18, 6, 12), 1)
draw_scaled_rect(sprite, SKIN_GREY, (32, 18, 6, 12))
draw_scaled_rect(sprite, BLACK, (32, 18, 6, 12), 1)

# Hands
draw_scaled_rect(sprite, SKIN_GREY, (0, 18, 4, 4))
draw_scaled_rect(sprite, BLACK, (0, 18, 4, 4), 1)
draw_scaled_rect(sprite, SKIN_GREY, (36, 18, 4, 4))
draw_scaled_rect(sprite, BLACK, (36, 18, 4, 4), 1)

# Legs
draw_scaled_rect(sprite, PANTS_BROWN, (12, 32, 6, 8))
draw_scaled_rect(sprite, PANTS_BROWN, (22, 32, 6, 8))
draw_scaled_rect(sprite, BLACK, (12, 32, 6, 8), 1)
draw_scaled_rect(sprite, BLACK, (22, 32, 6, 8), 1)

icon_path = os.path.join(os.path.dirname(__file__), "zombie_icon.png")
pygame.image.save(sprite, icon_path)
print(f"✓ Game-accurate zombie icon created: {icon_path}")
pygame.quit()
