"""Diagnostic script to check collision bounds."""

import sys
sys.path.insert(0, 'src')

from zombie import Zombie
from projectile import Projectile
from models import Vector2
import pygame

pygame.init()

print("="*60)
print("COLLISION BOUNDS DIAGNOSTIC")
print("="*60)

# Create zombie at (100, 100)
zombie = Zombie('z1', 'TestZombie', Vector2(100, 100), '123')
zombie.is_hidden = False
zombie.is_quarantining = False

# Create projectile at (90, 100) moving right
projectile = Projectile(Vector2(90, 100), Vector2(1, 0), 10)

print(f"\nZombie position: ({zombie.position.x}, {zombie.position.y})")
print(f"Zombie size: {zombie.width}x{zombie.height}")
zombie_bounds = zombie.get_bounds()
print(f"Zombie bounds: {zombie_bounds}")
print(f"  left={zombie_bounds.left}, right={zombie_bounds.right}")
print(f"  top={zombie_bounds.top}, bottom={zombie_bounds.bottom}")

print(f"\nProjectile position: ({projectile.position.x}, {projectile.position.y})")
print(f"Projectile radius: {projectile.radius}")
proj_bounds = projectile.get_bounds()
print(f"Projectile bounds: {proj_bounds}")
print(f"  left={proj_bounds.left}, right={proj_bounds.right}")
print(f"  top={proj_bounds.top}, bottom={proj_bounds.bottom}")

print(f"\nDo bounds overlap? {proj_bounds.colliderect(zombie_bounds)}")

# Calculate distance
dx = zombie.position.x - projectile.position.x
dy = zombie.position.y - projectile.position.y
distance = (dx*dx + dy*dy) ** 0.5
print(f"Distance between centers: {distance:.2f} pixels")

print("\n" + "="*60)
print("ANALYSIS")
print("="*60)
if proj_bounds.colliderect(zombie_bounds):
    print("✅ Bounds DO overlap - collision should be detected")
else:
    print("❌ Bounds DO NOT overlap - this is why collision fails!")
    print(f"   Projectile needs to be within {zombie.width/2 + projectile.radius} pixels")
    print(f"   Current distance: {distance:.2f} pixels")
