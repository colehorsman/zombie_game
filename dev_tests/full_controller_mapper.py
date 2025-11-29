#!/usr/bin/env python3
"""
Complete Controller Mapper for SN30 Pro
Detects ALL inputs: buttons, axes, hats, and any other events.
Press ESC to exit.
"""

import pygame
import sys

pygame.init()
pygame.joystick.init()

# Create window
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Complete Controller Mapper - Press ANY button/input")

font = pygame.font.Font(None, 28)
small_font = pygame.font.Font(None, 20)
title_font = pygame.font.Font(None, 36)

# Track all inputs
events_log = []
MAX_LOG = 20

# Initialize controller
joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"🎮 Controller: {joystick.get_name()}")
    print(f"   Buttons: {joystick.get_numbuttons()}")
    print(f"   Axes: {joystick.get_numaxes()}")
    print(f"   Hats: {joystick.get_numhats()}")
    print(f"   Balls: {joystick.get_numballs()}")
else:
    print("❌ No controller detected!")

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        
        # Log ALL joystick events
        elif event.type == pygame.JOYBUTTONDOWN:
            msg = f"BUTTON DOWN: {event.button}"
            events_log.append(msg)
            print(f"🔘 {msg}")
        elif event.type == pygame.JOYBUTTONUP:
            msg = f"BUTTON UP: {event.button}"
            events_log.append(msg)
            print(f"⚪ {msg}")
        elif event.type == pygame.JOYAXISMOTION:
            # Only log significant axis changes
            if abs(event.value) > 0.5:
                msg = f"AXIS {event.axis}: {event.value:.2f}"
                events_log.append(msg)
                print(f"📊 {msg}")
        elif event.type == pygame.JOYHATMOTION:
            msg = f"HAT {event.hat}: {event.value}"
            events_log.append(msg)
            print(f"🎯 {msg}")
        elif event.type == pygame.JOYBALLMOTION:
            msg = f"BALL {event.ball}: {event.rel}"
            events_log.append(msg)
            print(f"⚽ {msg}")
        elif event.type == pygame.JOYDEVICEADDED:
            msg = "DEVICE ADDED"
            events_log.append(msg)
            print(f"➕ {msg}")
        elif event.type == pygame.JOYDEVICEREMOVED:
            msg = "DEVICE REMOVED"
            events_log.append(msg)
            print(f"➖ {msg}")
    
    # Trim log
    if len(events_log) > MAX_LOG:
        events_log = events_log[-MAX_LOG:]

    # Clear screen
    screen.fill((20, 20, 30))
    
    # Title
    title = title_font.render("Complete Controller Mapper", True, (255, 255, 0))
    screen.blit(title, (250, 20))
    
    # Controller info
    if joystick:
        info_lines = [
            f"Controller: {joystick.get_name()}",
            f"Buttons: {joystick.get_numbuttons()} | Axes: {joystick.get_numaxes()} | Hats: {joystick.get_numhats()}",
        ]
        for i, line in enumerate(info_lines):
            text = small_font.render(line, True, (100, 255, 100))
            screen.blit(text, (50, 60 + i * 20))
    else:
        text = font.render("No controller detected!", True, (255, 100, 100))
        screen.blit(text, (50, 60))
    
    # Instructions
    inst = small_font.render("Press the STAR button (or any button) - watch console and screen", True, (200, 200, 200))
    screen.blit(inst, (50, 110))
    
    # Current state section
    pygame.draw.rect(screen, (40, 40, 50), (50, 140, 700, 180))
    state_title = font.render("CURRENT STATE (live polling)", True, (255, 200, 100))
    screen.blit(state_title, (60, 145))
    
    if joystick:
        # Show all button states
        y = 170
        buttons_text = "Buttons: "
        for i in range(joystick.get_numbuttons()):
            if joystick.get_button(i):
                buttons_text += f"[{i}] "
        if buttons_text == "Buttons: ":
            buttons_text += "(none pressed)"
        btn_surf = small_font.render(buttons_text, True, (100, 200, 255))
        screen.blit(btn_surf, (60, y))
        
        # Show all axis values
        y += 25
        axes_text = "Axes: "
        for i in range(joystick.get_numaxes()):
            val = joystick.get_axis(i)
            if abs(val) > 0.1:
                axes_text += f"[{i}:{val:.1f}] "
        if axes_text == "Axes: ":
            axes_text += "(centered)"
        axes_surf = small_font.render(axes_text, True, (100, 255, 200))
        screen.blit(axes_surf, (60, y))
        
        # Show all hat values
        y += 25
        hats_text = "Hats: "
        for i in range(joystick.get_numhats()):
            val = joystick.get_hat(i)
            if val != (0, 0):
                hats_text += f"[{i}:{val}] "
        if hats_text == "Hats: ":
            hats_text += "(centered)"
        hats_surf = small_font.render(hats_text, True, (255, 200, 100))
        screen.blit(hats_surf, (60, y))
    
    # Event log section
    pygame.draw.rect(screen, (40, 40, 50), (50, 330, 700, 250))
    log_title = font.render("EVENT LOG (recent inputs)", True, (255, 200, 100))
    screen.blit(log_title, (60, 335))
    
    for i, msg in enumerate(events_log[-12:]):
        color = (100, 200, 255) if "BUTTON" in msg else (100, 255, 200) if "AXIS" in msg else (255, 200, 100)
        text = small_font.render(msg, True, color)
        screen.blit(text, (60, 360 + i * 18))
    
    # Exit instruction
    exit_text = small_font.render("Press ESC to exit", True, (150, 150, 150))
    screen.blit(exit_text, (350, 580))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

print("\n" + "="*50)
print("SESSION SUMMARY")
print("="*50)
print(f"Total events logged: {len(events_log)}")
for msg in events_log:
    print(f"  {msg}")
