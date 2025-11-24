"""Shared pytest fixtures and configuration."""

import pytest
import sys
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def sample_zombie():
    """Create a sample zombie for testing."""
    from src.models import Vector2
    from src.zombie import Zombie
    
    return Zombie(
        identity_id="test-zombie-123",
        identity_name="test-user-1",
        position=Vector2(100, 100),
        account="123456789012"
    )


@pytest.fixture
def sample_projectile():
    """Create a sample projectile for testing."""
    from src.models import Vector2
    from src.projectile import Projectile
    
    return Projectile(
        position=Vector2(50, 100),
        velocity=Vector2(300, 0),
        damage=1
    )
