#!/usr/bin/env python3
"""Test script to check if models import correctly."""

import sys

sys.path.insert(0, "src")


def test_models():
    """Test that models import correctly with GenreType."""
    print("Testing models import...")

    from models import GameState, GameStatus, GenreType, TriggerType

    # Create game state
    gs = GameState(
        status=GameStatus.PLAYING,
        zombies_remaining=1,
        zombies_quarantined=0,
        total_zombies=1,
    )

    print(f"✅ GameState created")
    print(f"   current_genre: {gs.current_genre}")
    print(f"   genre_preferences: {gs.genre_preferences}")
    print(f"   is_story_mode: {gs.is_story_mode}")

    # Test GenreType enum
    print(f"\n✅ GenreType values:")
    for genre in GenreType:
        print(f"   {genre.name}: {genre.value}")

    print("\n✅ All models working correctly!")


if __name__ == "__main__":
    test_models()
