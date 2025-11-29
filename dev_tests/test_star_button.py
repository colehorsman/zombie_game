#!/usr/bin/env python3
"""
Quick test script to detect controller button presses.
Press the Star button 5 times to test - it will show the button number.
Press ESC or close window to exit.
"""

import pygame
import sys

pygame.init()
pygame.joystick.init()

# Create a small window
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Controller Button Test - Press Star 5x")

font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Track button presses
button_presses = []
running = True

# Initialize controller
joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"🎮 Controller detected: {joystick.get_name()}")
else:
    print("❌ No controller detected!")

clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.JOYBUTTONDOWN:
            button_presses.append(event.button)
            print(f"🔘 Button {event.button} pressed!")
            
            # Check if we have 5 presses
            if len(button_presses) >= 5:
                print(f"\n✅ 5 button presses recorded: {button_presses}")
                print(f"Most common button: {max(set(button_presses), key=button_presses.count)}")

    # Clear screen
    screen.fill((30, 30, 40))
    
    # Draw instructions
    title = font.render("Press the STAR button 5 times", True, (255, 255, 0))
    screen.blit(title, (100, 30))
    
    if joystick:
        controller_text = small_font.render(f"Controller: {joystick.get_name()}", True, (100, 255, 100))
    else:
        controller_text = small_font.render("No controller detected!", True, (255, 100, 100))
    screen.blit(controller_text, (100, 80))
    
    # Draw button press history
    history_title = small_font.render("Button presses:", True, (200, 200, 200))
    screen.blit(history_title, (100, 140))
    
    for i, btn in enumerate(button_presses[-10:]):  # Show last 10
        btn_text = font.render(f"Button {btn}", True, (100, 200, 255))
        screen.blit(btn_text, (100, 170 + i * 30))
    
    # Draw count
    count_text = font.render(f"Count: {len(button_presses)}/5", True, (255, 255, 255))
    screen.blit(count_text, (400, 140))
    
    # Draw exit instruction
    exit_text = small_font.render("Press ESC to exit", True, (150, 150, 150))
    screen.blit(exit_text, (100, 370))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("\n📊 Final results:")
print(f"All button presses: {button_presses}")
if button_presses:
    print(f"Star button is likely: {max(set(button_presses), key=button_presses.count)}")
