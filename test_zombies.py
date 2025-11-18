#!/usr/bin/env python3
"""Test zombie creation and positioning."""

import sys
sys.path.insert(0, 'src')

from models import Vector2
from zombie import Zombie

# Create a few test zombies
zombies = []
for i in range(5):
    zombie = Zombie(
        identity_id=f"test-{i}",
        identity_name=f"unused-identity-{i+1}",
        position=Vector2(200 + (i * 100), 100 + ((i % 5) * 80))
    )
    zombies.append(zombie)
    print(f"Zombie {i+1}: {zombie.identity_name} at ({zombie.position.x}, {zombie.position.y})")
    print(f"  Display number: {zombie.display_number}")
    print(f"  Sprite size: {zombie.width}x{zombie.height}")

print(f"\nTotal zombies created: {len(zombies)}")
print("Zombies are ready to render!")
