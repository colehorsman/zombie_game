#!/usr/bin/env python3
"""
Interactive Controller Mapper for Sonrai Zombie Blaster
Press buttons and see what number they are + current game mapping.
This helps identify which physical button = which number.
"""

import pygame
import sys

pygame.init()
pygame.joystick.init()

screen = pygame.display.set_mode((900, 700))
pygame.display.set_caption("Interactive Controller Mapper - Press buttons!")

font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 24)
title_font = pygame.font.Font(None, 42)
big_font = pygame.font.Font(None, 72)

# Current game mappings (what each button number does in the game)
GAME_MAPPINGS = {
    0: "A - Zap/Confirm",
    1: "B - Jump/Cancel", 
    2: "X - Screenshot 📸",
    3: "Y - Recording 🎬",
    4: "L1 - Unlock Combo",
    5: "R1 - Unlock Combo",
    6: "Select - Pause",
    7: "Start - Pause",
    8: "L3 - (unused)",
    9: "R3/Pause",
    10: "Star - Screenshot 📸",
    11: "D-Pad Up",
    12: "D-Pad Down",
    13: "D-Pad Left",
    14: "D-Pad Right",
}

# Track discovered mappings (button number -> physical label)
discovered = {}
last_button = None
last_button_time = 0

# Initialize controller
joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"🎮 Controller: {joystick.get_name()}")
    print(f"   Buttons: {joystick.get_numbuttons()}")
    print(f"   Axes: {joystick.get_numaxes()}")
else:
    print("❌ No controller!")

clock = pygame.time.Clock()
running = True

while running:
    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.JOYBUTTONDOWN:
            last_button = event.button
            last_button_time = current_time
            print(f"🔘 Button {event.button} pressed - Game function: {GAME_MAPPINGS.get(event.button, '(not mapped)')}")
        elif event.type == pygame.JOYAXISMOTION:
            if abs(event.value) > 0.8:
                print(f"📊 Axis {event.axis}: {event.value:.2f}")
        elif event.type == pygame.JOYHATMOTION:
            if event.value != (0, 0):
                print(f"🎯 Hat {event.hat}: {event.value}")

    # Clear screen
    screen.fill((25, 25, 35))
    
    # Title
    title = title_font.render("🎮 Controller Mapper", True, (255, 255, 0))
    screen.blit(title, (300, 20))
    
    # Controller info
    if joystick:
        info = small_font.render(f"Controller: {joystick.get_name()} | {joystick.get_numbuttons()} buttons", True, (100, 255, 100))
        screen.blit(info, (50, 70))
    
    # Last pressed button (big display)
    pygame.draw.rect(screen, (40, 40, 60), (50, 100, 800, 120), border_radius=10)
    
    if last_button is not None and current_time - last_button_time < 3000:
        btn_text = big_font.render(f"Button {last_button}", True, (100, 200, 255))
        screen.blit(btn_text, (80, 115))
        
        mapping = GAME_MAPPINGS.get(last_button, "(not mapped in game)")
        map_text = font.render(f"Game Function: {mapping}", True, (255, 200, 100))
        screen.blit(map_text, (80, 180))
    else:
        prompt = font.render("Press any button to see its number and game function...", True, (150, 150, 150))
        screen.blit(prompt, (150, 145))
    
    # Current mappings table
    pygame.draw.rect(screen, (35, 35, 50), (50, 240, 800, 400), border_radius=10)
    
    table_title = font.render("Current Game Button Mappings:", True, (255, 255, 255))
    screen.blit(table_title, (60, 250))
    
    # Draw mappings in columns
    col1_x, col2_x = 70, 470
    y_start = 290
    
    items = list(GAME_MAPPINGS.items())
    for i, (btn_num, desc) in enumerate(items):
        x = col1_x if i < 8 else col2_x
        y = y_start + (i % 8) * 35
        
        # Highlight if this was the last pressed button
        if btn_num == last_button and current_time - last_button_time < 3000:
            pygame.draw.rect(screen, (60, 80, 60), (x - 5, y - 2, 380, 30), border_radius=5)
            color = (100, 255, 100)
        else:
            color = (200, 200, 200)
        
        text = small_font.render(f"Button {btn_num:2d}: {desc}", True, color)
        screen.blit(text, (x, y))
    
    # Instructions
    inst1 = small_font.render("Press each button on your controller to see what number it is", True, (180, 180, 180))
    inst2 = small_font.render("This helps verify the mapping matches your physical controller", True, (180, 180, 180))
    inst3 = small_font.render("Press ESC to exit", True, (120, 120, 120))
    screen.blit(inst1, (200, 650))
    screen.blit(inst2, (200, 670))
    screen.blit(inst3, (380, 690))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("\n✅ Mapper closed")
