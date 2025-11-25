"""Diagnostic script to test collision detection bug."""

import sys
sys.path.insert(0, 'src')

from collision import check_collisions_with_spatial_grid, SpatialGrid
from zombie import Zombie
from projectile import Projectile
from models import Vector2

print("="*60)
print("COLLISION DETECTION DIAGNOSTIC")
print("="*60)

# Test 1: Normal zombie (should collide)
print("\nTest 1: Normal zombie (is_quarantining=False, is_hidden=False)")
zombie1 = Zombie('z1', 'TestZombie1', Vector2(100, 100), '123')
zombie1.is_hidden = False
zombie1.is_quarantining = False
proj1 = Projectile(Vector2(90, 100), Vector2(1, 0), 10)
grid1 = SpatialGrid(1280, 720)
collisions1 = check_collisions_with_spatial_grid([proj1], [zombie1], grid1)
print(f"  Zombie state: is_quarantining={zombie1.is_quarantining}, is_hidden={zombie1.is_hidden}")
print(f"  Collisions detected: {len(collisions1)}")
print(f"  ✅ EXPECTED: 1 collision" if len(collisions1) == 1 else f"  ❌ FAILED: Expected 1, got {len(collisions1)}")

# Test 2: Quarantining zombie (should NOT collide - this is the bug)
print("\nTest 2: Quarantining zombie (is_quarantining=True, is_hidden=False)")
zombie2 = Zombie('z2', 'TestZombie2', Vector2(100, 100), '123')
zombie2.is_hidden = False
zombie2.is_quarantining = True  # BUG: This flag makes zombie unshootable
proj2 = Projectile(Vector2(90, 100), Vector2(1, 0), 10)
grid2 = SpatialGrid(1280, 720)
collisions2 = check_collisions_with_spatial_grid([proj2], [zombie2], grid2)
print(f"  Zombie state: is_quarantining={zombie2.is_quarantining}, is_hidden={zombie2.is_hidden}")
print(f"  Collisions detected: {len(collisions2)}")
print(f"  ⚠️  BUG CONFIRMED: Zombie with is_quarantining=True is unshootable!" if len(collisions2) == 0 else f"  ✅ Fixed!")

# Test 3: Hidden zombie (should NOT collide - this is correct)
print("\nTest 3: Hidden zombie (is_quarantining=False, is_hidden=True)")
zombie3 = Zombie('z3', 'TestZombie3', Vector2(100, 100), '123')
zombie3.is_hidden = True
zombie3.is_quarantining = False
proj3 = Projectile(Vector2(90, 100), Vector2(1, 0), 10)
grid3 = SpatialGrid(1280, 720)
collisions3 = check_collisions_with_spatial_grid([proj3], [zombie3], grid3)
print(f"  Zombie state: is_quarantining={zombie3.is_quarantining}, is_hidden={zombie3.is_hidden}")
print(f"  Collisions detected: {len(collisions3)}")
print(f"  ✅ CORRECT: Hidden zombies should not collide" if len(collisions3) == 0 else f"  ❌ FAILED")

# Test 4: Both flags set (should NOT collide)
print("\nTest 4: Both flags set (is_quarantining=True, is_hidden=True)")
zombie4 = Zombie('z4', 'TestZombie4', Vector2(100, 100), '123')
zombie4.is_hidden = True
zombie4.is_quarantining = True
proj4 = Projectile(Vector2(90, 100), Vector2(1, 0), 10)
grid4 = SpatialGrid(1280, 720)
collisions4 = check_collisions_with_spatial_grid([proj4], [zombie4], grid4)
print(f"  Zombie state: is_quarantining={zombie4.is_quarantining}, is_hidden={zombie4.is_hidden}")
print(f"  Collisions detected: {len(collisions4)}")
print(f"  ✅ CORRECT: Both flags set should not collide" if len(collisions4) == 0 else f"  ❌ FAILED")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("The collision detection CORRECTLY skips zombies with is_quarantining=True")
print("This is BY DESIGN to prevent hitting zombies that are being eliminated.")
print("")
print("THE REAL BUG: Zombies are getting stuck with is_quarantining=True")
print("even though they should have this flag reset!")
print("")
print("SOLUTION: Reset is_quarantining flags after:")
print("  1. Quest completion (already fixed)")
print("  2. Quest failure (already fixed)")
print("  3. API errors (error handler should reset)")
print("  4. Returning to lobby (should reset all zombie states)")
print("="*60)
