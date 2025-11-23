#!/usr/bin/env python3
import pygame
import sys

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("❌ No controller detected")
    sys.exit(1)

j = pygame.joystick.Joystick(0)
j.init()

print(f"✅ Controller: {j.get_name()}")
print("Testing for 5 seconds - press any button or move stick...")

screen = pygame.display.set_mode((200, 100))
clock = pygame.time.Clock()

events_detected = []
for _ in range(300):  # 5 seconds at 60fps
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:
            events_detected.append(f"Button {event.button}")
        elif event.type == pygame.JOYAXISMOTION and abs(event.value) > 0.3:
            events_detected.append(f"Axis {event.axis}")

    if events_detected:
        break

    clock.tick(60)

pygame.quit()

if events_detected:
    print(f"✅ SUCCESS! Controller input working: {', '.join(set(events_detected))}")
else:
    print("❌ NO INPUT DETECTED - Check Input Monitoring permissions")
    print("   Go to: System Settings → Privacy & Security → Input Monitoring")
    print("   Enable permissions for your Terminal app")
